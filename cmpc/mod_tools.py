import json
import time
import logging as log
from pathlib import Path

import requests
import twitchio.errors
from cmpc.utils import send_webhook


CONFIG_FOLDER = Path('config')


class ModTools:
    def __init__(
            self, bot, ban_tools_on=True, timeout_tools_on=True, req_account_age_days=None, user_info_cache_path=None
    ):
        self.bot = bot
        self.ban_tools_on = ban_tools_on
        self.timeout_tools_on = timeout_tools_on

        if req_account_age_days is None:
            req_account_age_days = 7
        self.req_age_days = req_account_age_days
        if user_info_cache_path is None:
            user_info_cache_path = CONFIG_FOLDER / 'user_info_cache.json'
        self.cache_path = user_info_cache_path

        # Load cache to memory
        try:
            with open(self.cache_path) as user_info_cache_file:
                self.user_info_cache = json.load(user_info_cache_file)
            log.info('Loaded user info cache.')
        except (FileNotFoundError, json.JSONDecodeError):
            log.warning('User info cache did not exist or error decoding, initialising a new cache.')
            self.user_info_cache = {}

            with open(self.cache_path, 'w') as user_info_cache_file:
                json.dump(self.user_info_cache, user_info_cache_file)

    async def notify_ignored_user(self, message, cache_file_path=CONFIG_FOLDER / 'user_info_cache.json'):
        user_id = str(message.author.id)
        if not self.user_info_cache[user_id].get('notified_ignored'):
            ctx = await self.bot.get_context(message)
            # TODO: add custom messages depending on why they were ignored
            await ctx.send(f'@{message.author.name} your message was ignored by the script because '
                           f'your account is under {self.req_age_days} days old '
                           'or because you have been banned/timed out.')
            log.info('Notified user they were ignored.')

            self.user_info_cache[user_id]['notified_ignored'] = True
            with open(cache_file_path, 'w') as user_info_cache_file:
                json.dump(self.user_info_cache, user_info_cache_file)

    async def check_user_allowed(self, user_id, user_info_cache=None,
                                 cache_file_path=CONFIG_FOLDER / 'user_info_cache.json'):
        """Check whether a Twitch user account is old enough to run commands.

        Args:
            user_id -- Twitch account ID to get info on from their API
            cache_file_path -- JSON file to store info about users in. May be modified by this function.
        Returns a boolean which will be True if the user's account age was verified.

        Account age is checked against self.req_account_age_days.
        Also checks if the user has been manually banned or allowed.
        """
        # TODO: split into smaller functions e.g. check_user_cache and check_user_twitch_api?
        # TODO: for performance, backup the cache occasionally, instead of every write?
        if user_info_cache is None:
            user_info_cache = self.user_info_cache
        user_id = str(user_id)

        # If the user is in the cache get their info from the cache
        if user_id in user_info_cache:
            cached_user_info = user_info_cache[user_id]

            force_wait = cached_user_info.get('force_wait')
            # If they're marked as allow or block, return that
            if 'allow' in cached_user_info and not force_wait:
                return cached_user_info['allow']
            # If they're not marked, check the cached allow time
            elif time.time() > cached_user_info['allow_after']:
                user_info_cache[user_id]['allow'] = True
                if cached_user_info.get('force_wait'):
                    cached_user_info['force_wait'] = False
                with open(cache_file_path, 'w') as user_info_cache_file:
                    json.dump(user_info_cache, user_info_cache_file)

                return True
            else:
                return False
        # Else, try to get it from the Twitch API
        else:
            try:
                twitch_api_response = await self.bot.get_users(user_id)
                if not twitch_api_response:
                    raise twitchio.errors.HTTPException
                api_user_info = twitch_api_response[0]
            except requests.RequestException:
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

                user_info_cache[user_id] = {}
                if allow_after_time < time.time():
                    user_info_cache[user_id]['allow'] = True
                    return_value = True
                else:
                    user_info_cache[user_id]['allow_after'] = allow_after_time
                    return_value = False

                # Update the cache file
                with open(cache_file_path, 'w') as user_info_cache_file:
                    json.dump(user_info_cache, user_info_cache_file)

                return return_value

    async def process_commands(self, twitch_message):
        # User allow list handling commands
        if twitch_message.content.startswith((
                'script- ban', 'script- unban', 'script- approve',
                'script- timeout', 'script- untimeout',
                '../script ban', '../script unban', '../script approve',
                '../script timeout', '../script untimeout'
        )):
            args = twitch_message.content.split()
            subcommand = args[1]
            set_states = {}
            if subcommand in ['ban']:
                if not self.ban_tools_on:
                    return

                set_states = {
                    'allow': False,
                    'notified_ignored': False
                }
            elif subcommand in ['unban', 'approve']:
                set_states = {'allow': True}
            elif subcommand in ['timeout']:
                if not self.timeout_tools_on:
                    return

                try:
                    timeout_duration = float(args[3])
                except (IndexError, TypeError):
                    log.error('Error in timeout, no or invalid duration given.')
                    return

                timeout_end = time.time() + timeout_duration
                set_states = {
                    'allow_after': timeout_end,
                    'force_wait': True,
                    'notified_ignored': False
                }
            elif subcommand in ['untimeout']:
                set_states = {'force_wait': False}

            try:
                user_name = args[2]
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
                for key, value in set_states.items():
                    self.user_info_cache.setdefault(user_id, {})[key] = value

                with open(CONFIG_FOLDER / 'user_info_cache.json', 'w') as user_info_cache_file:
                    json.dump(self.user_info_cache, user_info_cache_file)
