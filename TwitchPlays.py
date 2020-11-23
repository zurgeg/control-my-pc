#!/usr/bin/env python

"""Let a twitch.tv chat room control a pc! Featuring permissions for mods and developers, discord integration.

Env vars:
    TWITCH_USERNAME -- Twitch account to log in as
    TWITCH_OAUTH_KEY -- authorisation for that twitch account
    DUKTHOSTING_API_KEY -- auth key to control a controlmybot instance on Dukt Hosting through a dev command
Files:
    config/apiconfig_static_backup.json -- automatically managed local backup of dev and mod lists from the API
    config/config.example.toml -- example config file with no keys, included in the git repo for reference
    config/config.toml -- real working instance of the config
    logs/chat.log -- every message sent in the connected Twitch chat
    logs/system.log -- mirror of the console output handled py the logging package
    executing.txt -- contains info about the currently executing command, for OBS
"""

# Due to my strong personal convictions,
# I wish to stress that this code in no
# way endorses a belief in the occult.

# PSL Packages;
import os  # file manager and .env handler, also runs cmd commands
import sys  # for exiting with best practices and getting exception info for log
import json  # json, duh,
import time  # for script- suspend command
import webbrowser  # el muchacho
import logging as log  # better print()
from pathlib import Path  # for best practices filepath handling

# PIP Packages;
import pyautogui
import requests  # api and discord webhooks
import toml  # configuration

# Local Packages;
import cmpc  # Pretty much all of the custom shit we need.


# Module level dunder names
__version__ = '3.6.0'

# Folders we use
CONFIG_FOLDER = Path('config/')
LOGS_FOLDER = Path('logs/')

# handle logging shit (copyright notice will remain on print)
# noinspection PyArgumentList
log.basicConfig(
    level=log.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        log.FileHandler(LOGS_FOLDER/'system.log', encoding='utf-8'),
        log.StreamHandler()
    ]
)
pyautogui.FAILSAFE = False

BRANCH_NAME, BRANCH_NAME_ASSUMED = cmpc.get_git_repo_info()
COPYRIGHT_NOTICE = f"""
------------------------------------------
           TWITCH PLAYS
           {BRANCH_NAME.upper()} BRANCH
           https://cmpc.live
           © 2020 controlmypc
           by CMPC Developers
------------------------------------------
"""
# Log copyright notice.
print(COPYRIGHT_NOTICE)

# Load configuration
log.debug('Stand by me.')
CONFIG = toml.load(CONFIG_FOLDER/'config.toml')
USER_AGENT = CONFIG['api']['useragent']
if CONFIG['twitch']['custom_channels_to_join']:
    CHANNELS_TO_JOIN = CONFIG['twitch']['channels_to_join']
else:
    CHANNELS_TO_JOIN = None
# Twitch channel name and oauth token from config will be overridden
# by env vars if they exist. This makes testing more streamlined.
if os.getenv('TWITCH_CHANNEL'):
    TWITCH_USERNAME = os.getenv('TWITCH_CHANNEL')
else:
    TWITCH_USERNAME = CONFIG['twitch']['channel']
if os.getenv('TWITCH_OAUTH_TOKEN'):
    TWITCH_OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
else:
    TWITCH_OAUTH_TOKEN = CONFIG['twitch']['oauth_token']
if os.getenv('DUKTHOSTING_API_KEY'):
    PANEL_API_KEY = os.getenv('DUKTHOSTING_API_KEY')
else:
    PANEL_API_KEY = CONFIG['api']['panelapikey']


class TwitchPlays(cmpc.TwitchConnection):
    """Implements functionality with permissions and some startup stuff."""

    def __init__(self, user, oauth, client_id, initial_channels):
        """Get set up, then call super().__init__.

        Args:
            same as cmpc.TwitchConnection.__init__ but without prefix
        Checks that username and auth are present. Deletes chat log if it exists. Instantiates a command processor
        and permissions handler.
        """
        # Check essential constants are not empty.
        if not TWITCH_USERNAME or not TWITCH_OAUTH_TOKEN:
            log.fatal('[TWITCH] No channel or oauth token was provided.')
            cmpc.send_webhook(CONFIG['discord']['systemlog'], 'FAILED TO START - No Oauth or username was provided.')
            sys.exit(2)
        if not PANEL_API_KEY:
            log.warning('[CHATBOT] No panel api key was provided, chatbot command has been disabled.')

        # Remove temp chat log if it exists.
        if os.path.exists(LOGS_FOLDER/'chat.log'):
            os.remove(LOGS_FOLDER/'chat.log')

        self.user_permissions_handler = self.permissions_handler_from_json()

        self.processor = cmpc.CommandProcessor(CONFIG, 'executing.txt')
        self.processor.log_to_obs(None)

        super().__init__(user, oauth, client_id, initial_channels)

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
            if apiconfig.status_code != 200:
                raise requests.RequestException
            else:
                apiconfig_json = json.loads(apiconfig.text)
                log.info('[API] Data here, and parsed!')

                # Save retrieved JSON to backup
                with open(static_backup_path, 'w') as static_backup_file:
                    json.dump(apiconfig_json, static_backup_file)
                log.info('[API] Backed up to static backup file')

        # If the request errored or response status code wasn't 200 'ok', use backup
        except requests.RequestException:
            log.warning('[API] Failed to load data from API')
            with open(static_backup_path, 'r') as static_backup_file:
                apiconfig_json = json.load(static_backup_file)

            log.info('[API] Loaded lists from static file instead')
            retrieved_time = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(static_backup_path.stat().st_mtime))
            log.warning('[API] One or multiple lists may be unavailable or incomplete/out of date\n'
                        f"JSON last updated: {apiconfig_json['last_updated']}\n"
                        f"Retrieved: {retrieved_time}")
            cmpc.send_webhook(CONFIG['discord']['systemlog'],
                              'Failed to load data from API\n'
                              'Loaded dev list from static file instead\n'
                              'One or multiple lists may be unavailable or incomplete/out of date\n'
                              f"Last updated: {apiconfig_json['last_updated']}\n"
                              f"Retrieved: {retrieved_time}\n\n"
                              f'[***Stream Link***](<https://twitch.tv/{TWITCH_USERNAME}>)\n'
                              f"**Environment -** {CONFIG['options']['DEPLOY']}"
                              )

        # Init and return user permissions handler from dev and mod lists
        return self.load_user_permissions(
            dev_list=apiconfig_json['devlist'],
            mod_list=apiconfig_json['modlist']
        )

    # TwitchConnection overrides
    async def event_ready(self):
        """Override TwitchConnection.event_ready - log and send discord webhook for startup message if applicable."""
        log.info("[TWITCH] Auth accepted and we are connected to twitch")
        # Send starting up message with webhook if in CONFIG.
        if CONFIG['options']['START_MSG']:
            cmpc.send_webhook(CONFIG['discord']['systemlog'],
                              'Script - **Online**\n'
                              f'[***Stream Link***](<https://twitch.tv/{TWITCH_USERNAME}>)\n'
                              f"**Environment -** {CONFIG['options']['DEPLOY']}",
                              )

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
            if twitch_message.username == 'controlmybot' or twitch_message.username == 'cmpclive':
                return

            # Process this beef
            command_has_run = self.processor.process_commands(twitch_message)
            if command_has_run:
                self.processor.log_to_obs(None)
                return

            user_permissions = self.user_permissions_handler.get(twitch_message.username, cmpc.Permissions())

            # Commands for authorised developers in dev list only.
            if user_permissions.script or user_permissions.developer:
                if twitch_message.content == 'script- testconn':
                    cmpc.send_webhook(CONFIG['discord']['modtalk'],
                                      'Connection made between twitch->script->webhook->discord')

                if twitch_message.content == 'script- reqdata':
                    context = {
                        'user': twitch_message.username,
                        'channel': TWITCH_USERNAME,
                        'modlist': [i for i, o in self.user_permissions_handler.items() if o.moderator],
                        'devlist': [i for i, o in self.user_permissions_handler.items() if o.developer],
                        'options': CONFIG['options'],
                    }
                    cmpc.send_data(CONFIG['discord']['modtalk'], context)

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
                    signal = self.processor.remove_prefix(twitch_message.original_content, 'chatbot- ')
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
                        'content': self.processor.remove_prefix(twitch_message.original_content, 'modsay '),
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

                if twitch_message.content in ['el muchacho']:
                    # os.system('vlc -f --no-repeat --no-osd --no-play-and-pause '
                    #           '"https://www.youtube.com/watch?v=GdtuG-j9Xog" vlc://quit')
                    webbrowser.open('https://www.youtube.com/watch?v=GdtuG-j9Xog', new=1)

                if twitch_message.content in ['shutdownabort']:
                    os.system('shutdown -a')

                if twitch_message.content in ['version', 'version?']:
                    self.processor.log_to_obs(None, none_log_msg=f'Version {__version__} ({twitch_message.username})',
                                              sleep_duration=3.0, none_sleep=True)

                if twitch_message.content.startswith('script- suspend '):
                    duration = self.processor.remove_prefix(twitch_message.content, 'script- suspend ')
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

                if twitch_message.content.startswith('!defcon '):
                    severity = self.processor.remove_prefix(twitch_message.content, '!defcon ')

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
                        time.sleep(86400)
                    elif severity == 'blue':
                        # os.system('vlc -f --repeat --no-osd --no-play-and-pause '
                        #           '"https://www.youtube.com/watch?v=GdtuG-j9Xog"')
                        webbrowser.open('https://www.youtube.com/watch?v=GdtuG-j9Xog', new=1)
                        # custom_log_to_obs('[defcon BLUE, el muchacho de los ojos tristes]',
                        #                   twitch_message, self.processor)
                        self.processor.log_to_obs(None, none_log_msg='[defcon BLUE, el muchacho de los ojos tristes]'
                                                                     f' ({twitch_message.username})')
                        time.sleep(30)

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
                            twitch_message, TWITCH_USERNAME,
                            CONFIG['options']['DEPLOY'], BRANCH_NAME, BRANCH_NAME_ASSUMED)


if __name__ == '__main__':
    twitch_client = TwitchPlays(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN, USER_AGENT, CHANNELS_TO_JOIN)
    twitch_client.run()
