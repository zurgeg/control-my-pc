#!/usr/bin/env python

"""Let a twitch.tv chat room control a pc! Featuring permissions system, discord integration, and a whole lot more.

Files:
    config/apiconfig_static_backup.json -- automatically managed local backup of dev and mod lists from the API
    config/config.example.toml -- example config file with no keys, included in the git repo for reference
    config/config.toml -- real working instance of the config
    logs/chat.log -- every message sent in the connected Twitch chat
    logs/system.log -- mirror of the console output handled by the logging package
    executing.txt -- contains info about the currently executing command, for OBS
"""

# Due to my strong personal convictions,
# I wish to stress that this code in no
# way endorses a belief in the occult.

# PSL Packages;
import os  # file manager and cmd command handler
import sys  # for exiting with best practices and getting exception info for log
import json  # json, duh,
import time  # for script- suspend command
import argparse
import logging as log  # better print()
from pathlib import Path  # for best practices filepath handling

# PIP Packages;
import pyautogui  # some mod only commands
import requests  # api and discord webhooks
import toml  # configuration
import twitchio.ext.commands.bot

# Local Packages;
import cmpc  # Pretty much all of the custom shit we need.

__version__ = '3.9.0'

# Folders we use
CONFIG_FOLDER = Path('config/')
LOGS_FOLDER = Path('logs/')

pyautogui.FAILSAFE = False

BRANCH_NAME, BRANCH_NAME_ASSUMED = cmpc.get_git_repo_info()
COPYRIGHT_NOTICE = f"""
------------------------------------------
           TWITCH PLAYS
           {BRANCH_NAME.upper()} BRANCH
           https://cmpc.live
           © 2020-2021 controlmypc
           by CMPC Developers
------------------------------------------
"""

# Load configuration
# noinspection PyArgumentList
CONFIG = toml.load(CONFIG_FOLDER/'config.toml')
# noinspection PyArgumentList
log.basicConfig(
    level=f'{CONFIG["options"]["LOGGER_LEVEL"].upper()}',
    format='[%(levelname)s] %(message)s',
    handlers=[
        log.FileHandler(LOGS_FOLDER/'system.log', encoding='utf-8'),
        log.StreamHandler()
    ]
)
# TODO: remove unnecessary or modified constants
log.debug('Stand by me.')
USER_AGENT = CONFIG['api']['useragent']
CHANNEL_TO_JOIN = CONFIG['twitch']['channel_to_join']
TWITCH_USERNAME = CONFIG['twitch']['username']
TWITCH_OAUTH_TOKEN = CONFIG['twitch']['oauth_token']
if not TWITCH_OAUTH_TOKEN.startswith('oauth:'):
    TWITCH_OAUTH_TOKEN = 'oauth:' + TWITCH_OAUTH_TOKEN
TWITCH_CLIENT_ID = CONFIG['twitch']['api_client_id']
PANEL_API_KEY = CONFIG['api']['panelapikey']
parser = argparse.ArgumentParser(description='Let a twitch.tv chat room control a pc! Featuring permissions system, '
                                             'discord integration, and a whole lot more.',
                                 epilog='For more help check the module docstring, and the readme, which also '
                                        'features a link to the wiki.')
parser.add_argument('--version', action='version', version=__version__)
parser.add_argument('--offline-mode', action='store_true')
cliargs = parser.parse_args()


class TwitchPlays(twitchio.ext.commands.bot.Bot):
    """Implements functionality with permissions and some startup stuff."""

    def __init__(self, user, oauth, client_id, initial_channel, modtools_on=False):
        """Get set up, then call super().__init__.

        Args:
            same as cmpc.TwitchConnection.__init__ but without prefix
        Checks that username and auth are present. Deletes chat log if it exists. Instantiates a command processor
        and permissions handler.
        """
        self.modtools_on = modtools_on

        # Check essential constants are not empty.
        if not TWITCH_USERNAME or not TWITCH_OAUTH_TOKEN:
            log.fatal('[TWITCH] No channel or oauth token was provided.')
            cmpc.send_webhook(CONFIG['discord']['systemlog'], 'FAILED TO START - No Oauth or username was provided.')
            sys.exit(2)
        if not PANEL_API_KEY:
            log.warning('[CHATBOT] No panel api key was provided, chatbot command has been disabled.')
        if CONFIG['options']['LOGGER_LEVEL'].lower() == "debug" and CONFIG['options']['DEPLOY'] == "Production":
            log.warning('[LOG] You are enabling debug mode in a production env, '
                        'this will log discord webhook urls to system.log and such. you have been warned.')

        # Remove temp chat log if it exists.
        if os.path.exists(LOGS_FOLDER/'chat.log'):
            os.remove(LOGS_FOLDER/'chat.log')

        # Load cache to memory
        try:
            if not os.path.isfile(CONFIG_FOLDER/'user_info_cache.json'):
                raise FileNotFoundError('User info cache does not exist.')

            with open(CONFIG_FOLDER/'user_info_cache.json', 'r') as user_info_cache_file:
                self.user_info_cache = json.load(user_info_cache_file)
                log.info('Loaded user info cache.')
        except (FileNotFoundError, json.JSONDecodeError):
            log.warning('User info cache did not exist or error decoding, initialising a new cache.')
            self.user_info_cache = {}

            with open(CONFIG_FOLDER/'user_info_cache.json', 'w') as user_info_cache_file:
                json.dump(self.user_info_cache, user_info_cache_file)

        self.user_permissions_handler = self.permissions_handler_from_json()

        self.processor = cmpc.CommandProcessor(CONFIG, 'executing.txt')
        self.processor.log_to_obs(None)
        if cliargs.offline_mode:
            self.script_tester = cmpc.ScriptTester(TwitchPlays.event_message, self)
        else:
            super().__init__(irc_token=oauth, client_id=client_id, nick=user,
                             prefix='!', initial_channels=[initial_channel])

    @property
    def tester(self):
        return self.script_tester

    # TwitchPlays methods - TwitchConnection overrides below
    @staticmethod
    def load_user_permissions(dev_list, mod_list):
        """Generate a dict of user permissions based on lists of devs and mods.

        Args:
            dev_list, mod_list -- self explanatory
        Returns:
            user_permissions -- the aforementioned dict
        """
        user_permissions = {}
        for dev in dev_list:
            perms = user_permissions.get(dev, cmpc.Permissions())
            perms.developer = True
            user_permissions[dev] = perms
        for mod in mod_list:
            perms = user_permissions.get(mod, cmpc.Permissions())
            perms.moderator = True
            user_permissions[mod] = perms
        user_permissions.setdefault('cmpcscript', cmpc.Permissions()).script = True

        return user_permissions

    def permissions_handler_from_json(self,
                                      url=CONFIG['api']['apiconfig'],
                                      static_backup_path=CONFIG_FOLDER / 'apiconfig_static_backup.json'):
        """Init a cmpc.Permissions object after retrieving source dev and mod lists.

        Args:
            url -- the url to attempt to retrieve JSON from
            static_backup_path -- path to the static backup local JSON file
        Returns:
            a cmpc.Permissions object generated with load_user_permissions
        If retrieval from the url is successful, it will be backed up to the local file.
        Otherwise, if retrieval is unsuccessful, the local file will be used instead, and warnings will be logged.
        The warnings include information about when the local file was updated and retrieved.
        """
        # Attempt get dev and mod lists from API.
        log.info('[API] Requesting data!')
        try:
            apiconfig = requests.get(url)
            if not apiconfig.ok:
                raise requests.RequestException
            else:
                apiconfig_json = apiconfig.json()
                log.info('[API] Data here, and parsed!')

                # Save retrieved JSON to backup
                with open(static_backup_path, 'w') as static_backup_file:
                    json.dump(apiconfig_json, static_backup_file)
                log.info('[API] Backed up to static backup file')

        # If the request errored or response status code wasn't 200 'ok', use backup
        except (requests.RequestException, json.JSONDecodeError):
            log.warning('[API] Failed to load data from API')
            with open(static_backup_path, 'r') as static_backup_file:
                apiconfig_json = json.load(static_backup_file)

            log.info('[API] Loaded lists from static file instead')
            retrieved_time = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(static_backup_path.stat().st_mtime))
            try:
                log.warning('[API] One or multiple lists may be unavailable or incomplete/out of date\n'
                            f"    JSON last updated: {apiconfig_json['last_updated']}\n"
                            f"    Retrieved: {retrieved_time}")
                # noinspection PyUnboundLocalVariable
                cmpc.send_webhook(CONFIG['discord']['systemlog'],
                                  'Failed to load data from API\n'
                                  'Loaded dev list from static file instead\n'
                                  'One or multiple lists may be unavailable or incomplete/out of date\n'
                                  f"Last updated: {apiconfig_json['last_updated']}\n"
                                  f"Retrieved: {retrieved_time}\n\n"
                                  f'[***Stream Link***](<https://twitch.tv/{TWITCH_USERNAME}>)\n'
                                  f"**Environment -** {CONFIG['options']['DEPLOY']}\n"
                                  f"**Response Status Code- ** {apiconfig.status_code}"
                                  )
            except TypeError:
                log.warning('Your apiconfig backup is out of date and missing some fields. Trying to run anyway.')

        # Init and return user permissions handler from dev and mod lists
        return self.load_user_permissions(
            dev_list=apiconfig_json['devlist'],
            mod_list=apiconfig_json['modlist']
        )

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

    # TwitchConnection overrides
    async def event_ready(self):
        """Override TwitchConnection.event_ready - log and send discord webhook for startup message if applicable."""
        log.info("[TWITCH] Auth accepted and we are connected to twitch")
        # Send starting up message with webhook if in CONFIG.
        if CONFIG['options']['START_MSG']:
            cmpc.send_webhook(CONFIG['discord']['systemlog'],
                              'Script - **Online**\n'
                              f"[***Stream Link***](<https://twitch.tv/{CONFIG['channel_to_join']}>)\n"
                              f"**Environment -** {CONFIG['options']['DEPLOY']}",
                              )

    # noinspection PyUnboundLocalVariable
    async def event_message(self, message):
        """Override TwitchPlays.event_message - process a message.

        Args:
            message -- a twitchio.Message object
        Returns nothing
        Will run message through the command processor, returning if a command is found.
        Additionally looks for and executes some permission based commands, this might be refactored in the future.
        Also responsible for logging to obs, log files and discord webhooks if applicable.
        """
        twitch_message = cmpc.TwitchMessage(message.content, message.author.name)

        # Command processing is very scary business - let's wrap the whole thing in a try/catch
        # NO, BAD
        # TODO - remove try-except here
        try:
            # Log the chat if that's something we want to do
            if CONFIG['options']['LOG_ALL']:
                log.info(f'CHAT LOG: {twitch_message.get_log_string()}')
            if CONFIG['options']['LOG_PPR']:
                with open(LOGS_FOLDER/'chat.log', 'a', encoding='utf-8') as f:
                    f.write(f'{twitch_message.get_log_string()}\n')

            # Ignore bot messages
            if twitch_message.username in ['controlmybot', 'cmpclive', 'cmpcserver']:
                log.info(f'Ignored message from {twitch_message.username} due to exemption.')
                return
            # Ignore echo messages
            if not message.author.id:
                return

            user_permissions = self.user_permissions_handler.get(twitch_message.username, cmpc.Permissions())

            if self.modtools_on:
                # Check if the user is allowed to run commands
                # Don't bother checking for moderators or developers
                if not user_permissions.moderator or user_permissions.developer:
                    if not self.processor.check_user_allowed(message.author.id, self.user_info_cache):
                        await self.notify_ignored_user(message)
                        log.info(f'Ignored message from {twitch_message.username} due to account age or deny list.')
                        return

            # Process this beef
            command_has_run = self.processor.process_commands(twitch_message)
            if command_has_run:
                self.processor.log_to_obs(None)
                return

            # Commands for authorised developers in dev list only.
            if user_permissions.script or user_permissions.developer:
                if twitch_message.content == 'script- testconn':
                    cmpc.send_webhook(CONFIG['discord']['systemlog'],
                                      'Connection made between twitch->script->webhook->discord')

                if twitch_message.content == 'script- reqdata':
                    context = {
                        'user': twitch_message.username,
                        'channel': CONFIG['twitch']['channel_to_join'],
                        'modlist': [i for i, o in self.user_permissions_handler.items() if o.moderator],
                        'devlist': [i for i, o in self.user_permissions_handler.items() if o.developer],
                        'options': CONFIG['options'],
                    }
                    cmpc.send_data(CONFIG['discord']['systemlog'], context)

                if twitch_message.content == 'script- apirefresh':
                    self.user_permissions_handler = self.permissions_handler_from_json()
                    log.info('[API] refreshed user permissions from API')
                    cmpc.send_webhook(CONFIG['discord']['systemlog'], 'User permissions were refreshed from API.')

                if twitch_message.content == 'script- forceerror':
                    cmpc.send_error(CONFIG['discord']['systemlog'], 'Forced error!',
                                    twitch_message, TWITCH_USERNAME,
                                    CONFIG['options']['DEPLOY'], BRANCH_NAME, BRANCH_NAME_ASSUMED)

                if twitch_message.original_content.startswith('chatbot- '):
                    if not PANEL_API_KEY:
                        log.error('[CHATBOT] Command ran and no API key, '
                                  'skipping command and sending warning to discord.')
                        cmpc.send_webhook(CONFIG['discord']['systemlog'],
                                          'No chatbot api key was provided, skipping command.')
                        return
                    # IF YOU NEED AN API KEY, CONTACT MAX.
                    signal = cmpc.removeprefix(twitch_message.original_content, 'chatbot- ')
                    payload = {
                        "signal": signal
                    }
                    headers = {
                        'User-Agent': f'{USER_AGENT}',
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {PANEL_API_KEY}',
                    }
                    try:
                        x = requests.post(CONFIG['api']['panelapiendpoint'], json=payload, headers=headers)
                        cmpc.send_webhook(CONFIG['discord']['systemlog'],
                                          f'Chatbot control ran({signal}) and returned with a code of {x.status_code}')
                    except requests.RequestException:
                        log.error(f'Could not execute chatbot control: {twitch_message.original_content}',
                                  sys.exc_info())

            # Commands for authorized moderators in mod list only.
            if user_permissions.script or user_permissions.developer or user_permissions.moderator:
                if twitch_message.content.startswith('modsay '):
                    data = {
                        'username': twitch_message.username,
                        'content': cmpc.removeprefix(twitch_message.original_content, 'modsay '),
                    }
                    try:
                        requests.post(CONFIG['discord']['modtalk'],
                                      json=data, headers={'User-Agent': USER_AGENT})
                    except requests.RequestException:
                        log.error(f"Could not modsay this moderator's message: {twitch_message.original_content}",
                                  sys.exc_info())

                if twitch_message.content in ['hideall']:
                    pyautogui.hotkey('win', 'm')
                if twitch_message.content in ['mute']:
                    pyautogui.press('volumemute')

                if twitch_message.content in ['shutdownabort']:
                    os.system('shutdown -a')

                if twitch_message.content in ['script- version', 'version', 'version?']:
                    self.processor.log_to_obs(None, none_log_msg=f'Version {__version__} ({twitch_message.username})',
                                              sleep_duration=3.0, none_sleep=True)
                    log.info(f'Version {__version__} ({twitch_message.username})')

                if twitch_message.content.startswith('script- suspend '):
                    duration = cmpc.removeprefix(twitch_message.content, 'script- suspend ')
                    try:
                        duration = float(duration)
                    except ValueError:
                        log.error(f'Could not suspend for duration: {twitch_message.content}\nDue to non-numeric arg')
                        return
                    else:
                        try:
                            if duration == 1.0:
                                log_message = '[Suspend script for 1 second]'
                            else:
                                log_message = f'[Suspend script for {int(duration)} seconds]'
                            self.processor.log_to_obs(None, none_log_msg=f'{log_message} ({twitch_message.username})')
                            time.sleep(duration)
                        except ValueError:
                            log.error(f'Could not suspend for duration: {twitch_message.content}\nDue to negative arg')
                        except OverflowError:
                            log.error(f'Could not suspend for duration: {twitch_message.content}\n'
                                      'Due to too large arg')

                # User allow list handling commands
                if twitch_message.content.startswith(('script- ban ', 'script- unban ', 'script- approve',
                                                      'script- timeout', 'script- untimeout')):
                    args = twitch_message.content.split()
                    subcommand = args[1]
                    if subcommand in ['ban']:
                        set_states = {
                            'allow': False,
                            'notified_ignored': False
                        }
                    elif subcommand in ['unban', 'approve']:
                        set_states = {'allow': True}
                    elif subcommand in ['timeout']:
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
                        user_id = cmpc.twitch_api_get_user(CONFIG['twitch']['api_client_id'],
                                                           cmpc.removeprefix(CONFIG['twitch']['oauth_token'], 'oauth:'),
                                                           user_name=user_name)['id']
                    except requests.RequestException:
                        log.error(f'Unable to unban/ban user {user_name} - user not found!')
                    else:
                        for key, value in set_states.items():
                            self.user_info_cache.setdefault(user_id, {})[key] = value

                        with open(CONFIG_FOLDER/'user_info_cache.json', 'w') as user_info_cache_file:
                            json.dump(self.user_info_cache, user_info_cache_file)

                if twitch_message.content.startswith('!defcon '):
                    severity = cmpc.removeprefix(twitch_message.content, '!defcon ')

                    if severity == '1':
                        pyautogui.hotkey('win', 'm')
                        pyautogui.press('volumemute')
                        os.system('shutdown -s -t 0 -c "!defcon 1 -- emergency shutdown" -f -d u:5:19')
                        # custom_log_to_obs('[defcon 1, EMERGENCY SHUTDOWN]', twitch_message, self.processor)
                        self.processor.log_to_obs(None, none_log_msg='[defcon 1, EMERGENCY SHUTDOWN]')
                        time.sleep(999999)
                    # TODO: Add !defcon 2 -- close all running programs
                    elif severity == '3':
                        pyautogui.hotkey('win', 'm')
                        pyautogui.press('volumemute')
                        # custom_log_to_obs('[defcon 3, suspend script]', twitch_message, self.processor)
                        self.processor.log_to_obs(None, none_log_msg='[defcon 3, suspend script]'
                                                                     f' ({twitch_message.username})')
                        time.sleep(600)

            # Commands for cmpcscript only.
            if user_permissions.script:
                print(f'CMPC SCRIPT: {twitch_message.content}')
                if hash(twitch_message.original_content) == -111040882105999023:
                    sys.exit(1)

            self.processor.log_to_obs(None)

        except Exception as error:
            # Send error data to systemlog.
            log.error(f'{error}', sys.exc_info())
            cmpc.send_error(CONFIG['discord']['systemlog'], error,
                            twitch_message, CONFIG['twitch']['channel_to_join'],
                            CONFIG['options']['DEPLOY'], BRANCH_NAME, BRANCH_NAME_ASSUMED)

    # I don't know why this method is classed as necessary to implement but here it is.
    async def event_pubsub(self, data):
        """Override Bot.event_pubsub - do nothing (:."""
        pass


if __name__ == '__main__':
    # Log copyright notice.
    print(COPYRIGHT_NOTICE)
    twitch_client = TwitchPlays(user=TWITCH_USERNAME, oauth=TWITCH_OAUTH_TOKEN, client_id=TWITCH_CLIENT_ID,
                                initial_channel=CHANNEL_TO_JOIN)
    if cliargs.offline_mode:
        log.info("[Script] Starting script in offline only mode. Cya later internet.")
        twitch_client.tester.startTester()
    else:
        twitch_client.run()
