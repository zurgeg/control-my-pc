import json
import time
from pathlib import Path


CONFIG_FOLDER =


class ModFeatures:
    async def notify_ignored_user(self, message, cache_file_path=CONFIG_FOLDER / 'user_info_cache.json'):
        user_id = str(message.author.id)
        if not self.user_info_cache[user_id].get('notified_ignored'):
            ctx = await self.get_context(message)
            # TODO: add custom messages depending on why they were ignored
            await ctx.send(f'@{message.author.name} your message was ignored by the script because '
                           f'your account is under {self.processor.req_account_age_days} days old '
                           'or because you have been banned/timed out.')
            log.info('Notified user they were ignored.')

            self.user_info_cache[user_id]['notified_ignored'] = True
            with open(cache_file_path, 'w') as user_info_cache_file:
                json.dump(self.user_info_cache, user_info_cache_file)

    async def check_user_allowed(self, user_id, user_info_cache,
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
                allow_after_time = account_created_seconds + (self.req_account_age_days * 24 * 60 ** 2)

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
