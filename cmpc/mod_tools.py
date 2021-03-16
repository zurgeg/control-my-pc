import time
import sqlite3
import logging as log
from pathlib import Path
from typing import Union

import twitchio.errors
from cmpc.utils import send_webhook


CONFIG_FOLDER = Path('config')


class ModTools:
    def __init__(self, bot, ban_tools_on=True, timeout_tools_on=True, req_account_age_days=None):
        self.bot = bot
        self.ban_tools_on = ban_tools_on
        self.timeout_tools_on = timeout_tools_on

        if req_account_age_days is None:
            req_account_age_days = 7
        self.req_age_days = req_account_age_days

        self.cache_db_paths = [':memory:', CONFIG_FOLDER / 'user_info_cache.db']
        self.cache_db_pairs = self.init_dbs()

    def init_dbs(self):
        conn_cur_pairs = []
        for db_path in self.cache_db_paths:
            create_table = False
            if db_path == ':memory:':
                create_table = True
            elif not db_path.is_file():
                create_table = True

            conn = sqlite3.connect(db_path)
            cur = conn.cursor()

            if create_table:
                cur.execute("""CREATE TABLE users
(id INT PRIMARY KEY, allow BOOL, allow_after FLOAT, notified_ignored BOOL);""")
                conn.commit()
                log.info(f'Initialised user info cache {db_path}')
            else:
                log.info(f'Connected to user info cache {db_path}')

            conn_cur_pairs.append((conn, cur))

        return conn_cur_pairs

    def write_to_dbs(self, sql, data, db_pairs=None):
        if db_pairs is None:
            db_pairs = self.cache_db_pairs

        for conn, cur in db_pairs:
            cur.execute(sql, data)
            conn.commit()

    def read_from_dbs(self, user_id, db_pairs=None):
        if db_pairs is None:
            db_pairs = self.cache_db_pairs

        for index, pair in enumerate(db_pairs):
            conn, cur = pair
            response = cur.execute('SELECT * FROM users WHERE id=?', user_id)
            if response:
                self.write_to_dbs('INSERT INTO users VALUES ?', response, db_pairs=self.cache_db_pairs[:index])
                return response

        return None

    def get_user_info(self, user_id):
        cache_hit = self.read_from_dbs(user_id)
        if cache_hit is not None:
            return cache_hit
        else:
            try:
                twitch_api_response = await self.bot.get_users(user_id)
                if not twitch_api_response:
                    raise twitchio.errors.HTTPException
                api_user_info = twitch_api_response[0]
                log.debug(f'User ID {user_id} created at {api_user_info.created_at}')
            except twitchio.errors.HTTPException:
                # No luck, no allow
                send_webhook(self.bot.config['discord']['systemlog'],
                             f"Failed to get info on user from twitch api.")
                return False
            else:
                # Check the status from the response info, and save it to the cache
                account_created_string = api_user_info.created_at
                account_created_seconds = time.mktime(time.strptime(account_created_string, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # allow_after should be the time in seconds since the epoch after which the user is allowed
                allow_after_time = account_created_seconds + (self.req_age_days * 24 * 60 ** 2)

                self.write_to_dbs('INSERT INTO users(id, allow_after), VALUES (?, ?)', (user_id, allow_after_time))
                return self.read_from_dbs(user_id)

    async def notify_ignored_user(self, message):
        user_id = message.author.id
        user_info = self.read_from_dbs(user_id)
        # user_info [3] = notified_ignored
        if not user_info[3]:
            ctx = await self.bot.get_context(message)
            # TODO: add custom messages depending on why they were ignored
            await ctx.send(f'@{message.author.name} your message was ignored by the script because '
                           f'your account is under {self.req_age_days} days old '
                           'or because you have been banned/timed out.')
            log.info('Notified user they were ignored.')

            self.write_to_dbs('UPDATE users SET notified_ignored=true WHERE user_id=?', user_id)

    async def check_user_allowed(self, user_id):
        user_info: Union[bool, tuple] = self.get_user_info(user_id)
        if not user_info:
            return user_info
        elif user_info[1] is not None:
            return user_info[1]
        else:
            return user_info[2] < time.time()

    async def process_commands(self, twitch_message):
        # User allow list handling commands
        if twitch_message.content.startswith(['script- ', '../script ']):
            args = twitch_message.content.split()
            try:
                subcommand = args[1]
            except IndexError:
                return

            set_states = []
            if subcommand in ['ban']:
                if not self.ban_tools_on:
                    return

                set_states = [
                    ('allow', False),
                    ('notified_ignored', False),
                ]
            elif subcommand in ['unban', 'approve']:
                set_states = [('allow', True)]
            elif subcommand in ['timeout']:
                if not self.timeout_tools_on:
                    return

                try:
                    timeout_duration = float(args[3])
                except (IndexError, TypeError):
                    log.error('Error in timeout, no or invalid duration given.')
                    return

                timeout_end = time.time() + timeout_duration
                set_states = [
                    ('allow', None),
                    ('allow_after', timeout_end),
                    ('notified_ignored', False),
                ]
            elif subcommand in ['untimeout']:
                set_states = [('allow_after', 0)]

            try:
                user_name = args[2].lstrip('@')
            except IndexError:
                log.error('Error in ban/timeout, no username given.')
                return

            try:
                twitch_api_response = await self.bot.get_users(user_name)
                if not twitch_api_response:
                    raise twitchio.errors.HTTPException
                user_id = twitch_api_response[0].id
            except twitchio.errors.HTTPException:
                log.error(f'Unable to unban/ban user {user_name} - user not found!')
            else:
                set_states = [t+user_id for t in set_states]
                self.write_to_dbs('UPDATE users SET ?=? WHERE id=?', set_states)
