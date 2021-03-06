import time
import sqlite3
import typing
import logging as log
from pathlib import Path
from typing import Union
from asyncio import Lock

import twitchio
from cmpc.utils import send_webhook
from cmpc.twitch_message import TwitchMessage


CONFIG_FOLDER = Path('config')
SCHEMA = {
    'id': 0,
    'allow': 1,
    'allow_after': 2,
    'notified_ignored': 3,
}
db_list_type = typing.List[typing.Tuple[sqlite3.Connection, sqlite3.Cursor]]


class ModTools:
    def __init__(
            self, bot,
            ban_tools_on: bool = True, timeout_tools_on: bool = True, req_account_age_days: float = None
    ):
        self.bot = bot
        self.ban_tools_on = ban_tools_on
        self.timeout_tools_on = timeout_tools_on

        if req_account_age_days is None:
            req_account_age_days = 7
        self.req_age_days = req_account_age_days

        self.cache_db_paths = [':memory:', CONFIG_FOLDER / 'user_info_cache.db']
        self.cache_db_pairs = self.init_dbs()
        self.db_access_lock = Lock()
        log.debug('Initialised ModTools object.')

    def init_dbs(self) -> db_list_type:
        """Return a list of (conn, cur) tuples based off self.cache_db_paths."""
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
                # todo: add account_created column in case we want to change the age requirement without invalidating
                #       the cache?
                cur.execute("""CREATE TABLE users
(id INT PRIMARY KEY, allow BOOL, allow_after FLOAT, notified_ignored BOOL)""")
                conn.commit()
                log.info(f'Initialised user info cache {db_path}')
            else:
                log.info(f'Connected to user info cache {db_path}')

            conn_cur_pairs.append((conn, cur))

        return conn_cur_pairs

    async def write_to_dbs(self, sql: str, data: typing.Iterable, db_pairs: db_list_type = None, many: bool = False):
        """Execute some sql on every cache database."""
        log.debug(f'Writing to some dbs {sql} {data} {db_pairs if db_pairs is None else len(db_pairs)}')
        if db_pairs is None:
            db_pairs = self.cache_db_pairs

        for conn, cur in db_pairs:
            if many:
                cur.executemany(sql, data)
            else:
                cur.execute(sql, data)
            async with self.db_access_lock:
                conn.commit()

    async def read_from_dbs(self, user_id: int, db_pairs=None):
        """Iterate through the databases for a result.

        If we get a result, it's then written to every database on which it wasn't found, to speed up getting
        that result next time.
        """
        log.debug(f'Reading from some dbs {user_id} {db_pairs if db_pairs is None else len(db_pairs)}')
        if db_pairs is None:
            db_pairs = self.cache_db_pairs

        for index, pair in enumerate(db_pairs):
            conn, cur = pair
            cur.execute('SELECT * FROM users WHERE id=?', (user_id,))
            response = cur.fetchone()
            if response:
                log.debug(f'Cache hit from {conn}')
                await self.write_to_dbs(
                    'INSERT INTO users VALUES (?,?,?,?)',
                    response, db_pairs=self.cache_db_pairs[:index]
                )
                return response

        log.debug('No cache hit')
        return None

    async def get_user_info(self, user_id: int):
        """Get info on a twitch user from their user id.

        First searches the cache databases, and if no result is found it gets the account age from the twitch api
        and creates a new entry in the databases, then returns that.
        """
        log.debug(f'Getting user info {user_id}')
        cache_hit = await self.read_from_dbs(user_id)
        if cache_hit is not None:
            return cache_hit
        else:
            try:
                twitch_api_response = await self.bot.get_users(user_id)
                if not twitch_api_response:
                    raise twitchio.HTTPException
                api_user_info = twitch_api_response[0]
                log.debug(f'User ID {user_id} created at {api_user_info.created_at}')
            except twitchio.HTTPException:
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

                await self.write_to_dbs('INSERT INTO users(id, allow_after) VALUES (?, ?)', (user_id, allow_after_time))
                return await self.read_from_dbs(user_id)

    async def notify_ignored_user(self, message: twitchio.Message):
        """Check if a user has been notified they're banned, if they haven't then do it.

        Also send a mod ping to notify to keep an eye on them

        Args:
            message -- the twitchio message to get the user id from and to reply to if necessary
        """
        user_id = message.author.id
        user_info = await self.read_from_dbs(user_id)
        # user_info [3] = notified_ignored
        if not user_info[3]:
            ctx = await self.bot.get_context(message)
            # todo: add custom messages depending on why they were ignored
            # and only send the mod webhook if it was because of account age
            await ctx.send(f'[SCRIPT] @{message.author.name} your message was ignored by the script because '
                           f'your account is under {self.req_age_days} days old '
                           'or because you have been banned/timed out.')
            log.info('Notified user they were ignored.')

            send_webhook(
                self.bot.config['discord']['modtalk'],
                f"{self.bot.config['discord']['modalertping']} twitch user @{message.author.name} was ignored "
                'because of account age. Keep an eye on them.'
            )
            log.info('Warned mods about ignored user via webhook.')

            await self.write_to_dbs('UPDATE users SET notified_ignored=? WHERE id=?', (True, user_id))

    async def check_user_allowed(self, user_id: int) -> bool:
        """Return True if a user can run commands and False otherwise.

        Gets their info, then checks whether they've been manually allowed or denied first.
        If they haven't been manually allowed or denied, checks the time they're allowed.
        """
        user_info: Union[bool, tuple] = await self.get_user_info(user_id)
        if not user_info:
            return user_info
        elif user_info[SCHEMA['allow']] is not None:
            return user_info[SCHEMA['allow']]
        else:
            return user_info[SCHEMA['allow_after']] < time.time()

    # todo: return True or False?
    async def process_commands(self, twitch_message: TwitchMessage):
        """Process ban/unban and timeout/untimeout commands."""
        # User allow list handling commands
        if twitch_message.content.startswith(('script- ', '../script ')):
            args = twitch_message.content.split()
            try:
                subcommand = args[1]
            except IndexError:
                return

            if subcommand in ['ban']:
                if not self.ban_tools_on:
                    return

                set_states = [
                    ['allow', False],
                    ['notified_ignored', False],
                ]
            elif subcommand in ['unban', 'approve']:
                set_states = [['allow', True]]
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
                    ['allow', None],
                    ['allow_after', timeout_end],
                    ['notified_ignored', False],
                ]
            elif subcommand in ['untimeout']:
                set_states = [['allow_after', 0]]
            else:
                return

            try:
                user_name = args[2].lstrip('@')
            except IndexError:
                log.error('Error in ban/timeout, no username given.')
                return

            try:
                twitch_api_response = await self.bot.get_users(user_name)
                if not twitch_api_response:
                    raise twitchio.errors.HTTPException
                user_id = int(twitch_api_response[0].id)
            except twitchio.errors.HTTPException:
                log.error(f'Unable to unban/ban user {user_name} - user not found!')
            else:
                current_user_info = await self.get_user_info(user_id)
                new_user_info = list(current_user_info)
                for key, value in set_states:
                    new_user_info[SCHEMA[key]] = value
                new_user_info.append(user_id)
                new_user_info.pop(0)

                await self.write_to_dbs(
                    'UPDATE users SET allow=?, allow_after=?, notified_ignored=? WHERE id=?',
                    new_user_info
                )
