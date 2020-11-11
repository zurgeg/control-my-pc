# PSL Packages;
import os  # file manager and .env handler, also runs cmd commands
import sys  # for exiting with best practices and getting exception info for log
import json  # json, duh,
import time  # for script- suspend command
import copy  # for copying objects - used for custom obs logs
import webbrowser  # el muchacho
import logging as log  # better print()

# PIP Packages;
import pyautogui  # only used in rawsend- command
import requests  # api and discord webhooks
import toml  # configuration
import git  # for automatic branch detection in the copyright message, `pip install gitpython`
from pynput.mouse import Controller  # Not really needed, but (I think) something still relies on it so /shrug

# Local Packages;
import cmpc  # Pretty much all of the custom shit we need.
# TODO: remove
# import TwitchPlays_Connection  # Connect to twitch via IRC.

# test
import tracemalloc
tracemalloc.start()


pyautogui.FAILSAFE = False

# Log copyright notice.
try:
    branch_name = git.Repo().active_branch.name
    branch_name_assumed = False
except git.exc.GitError:
    branch_name = 'master'
    branch_name_assumed = True
COPYRIGHT_NOTICE = f"""
------------------------------------------
           TWITCH PLAYS
           {branch_name.upper()} BRANCH
           https://cmpc.live
           © 2020 controlmypc
           by CMPC Developers
------------------------------------------
"""
print(COPYRIGHT_NOTICE)
# handle logging shit (copyright notice will remain on print)
# noinspection PyArgumentList
log.basicConfig(
    level=log.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        log.FileHandler('system.log', encoding='utf-8'),
        log.StreamHandler()
    ]
)
# Load Configuration
log.debug('Stand by me.')
config = toml.load('config.toml')
USER_AGENT = config['api']['useragent']
# Twitch channel name and oauth token from config will be overridden 
# by env vars if they exist. This makes testing more streamlined.
if os.getenv('TWITCH_CHANNEL'):
    TWITCH_USERNAME = os.getenv('TWITCH_CHANNEL')
else:
    TWITCH_USERNAME = config['twitch']['channel']
if os.getenv('TWITCH_OAUTH_TOKEN'):
    TWITCH_OAUTH_TOKEN = os.getenv('TWITCH_OAUTH_TOKEN')
else:
    TWITCH_OAUTH_TOKEN = config['twitch']['oauth_token']
if os.getenv('DUKTHOSTING_API_KEY'):
    PANEL_API_KEY = os.getenv('DUKTHOSTING_API_KEY')
else:
    PANEL_API_KEY = config['api']['panelapikey']


# Send starting up message with webhook if in config.
if config['options']['START_MSG']:
    cmpc.send_webhook(config['discord']['systemlog'],
                      'Script - **Online**\n'
                      f'[***Stream Link***](<https://twitch.tv/{TWITCH_USERNAME}>)\n'
                      f"**Environment -** {config['options']['DEPLOY']}",
                      )


def load_user_permissions(dev_list, mod_list):
    """Generate a dict of user permissions based on lists of devs and mods.

    Args:
        dev_list, mod_list -- self explanatory
    Returns:
        wip_user_permissions -- the aforementioned dict
    """
    wip_user_permissions = {}
    for dev in dev_list:
        perms = wip_user_permissions.get(dev, cmpc.Permissions())
        perms.developer = True
        wip_user_permissions[dev] = perms
    for mod in mod_list:
        perms = wip_user_permissions.get(mod, cmpc.Permissions())
        perms.moderator = True
        wip_user_permissions[mod] = perms
    wip_user_permissions.setdefault('cmpcscript', cmpc.Permissions()).script = True

    return wip_user_permissions


def mode_testing(environment, env_vars_used, branch):
    """Check if the script is in testing mode based on a number of factors.

    Args:
        environment -- DEPLOY constant from the config file, should be 'Production' or 'Debug'
        env_vars_used -- bool indicating if config has been pulled from environment variables
        branch -- the name of the git branch of the repo containing the script, if it exists
    Returns True if script should be in testing mode and False otherwise.
    """
    if environment == 'Debug' or env_vars_used or branch != 'master':
        return True
    else:
        return False


# Get dev and mod lists from API.
log.info('[API] Requesting data!')
apiconfig = requests.get(config['api']['apiconfig'])
if apiconfig.status_code == 200:
    apiconfig = json.loads(apiconfig.text)

    USER_PERMISSIONS = load_user_permissions(
        dev_list=apiconfig['devlist'],
        mod_list=apiconfig['modlist'],
    )
    log.info('[API] Data here, and parsed!')
else:
    log.warning('[API] Failed to load data from API')
    with open('staticdevlist.json', 'r') as static_dev_list_file:
        static_dev_list = json.load(static_dev_list_file)

    USER_PERMISSIONS = load_user_permissions(
        dev_list=static_dev_list,
        mod_list=[],
    )
    log.info('[API] Loaded dev list from static file instead')
    log.warning('[API] Mod list will be unavailable')
    cmpc.send_webhook(config['discord']['systemlog'],
                      'Failed to load data from API\n'
                      'Loaded dev list from static file instead\n'
                      'Mod list will be unavailable\n\n'
                      f'[***Stream Link***](<https://twitch.tv/{TWITCH_USERNAME}>)\n'
                      f"**Environment -** {config['options']['DEPLOY']}"
                      )


# Remove temp chat log or log if it doesn't exist.
if os.path.exists('chat.log'):
    os.remove('chat.log')

if not TWITCH_USERNAME or not TWITCH_OAUTH_TOKEN:
    log.fatal('[TWITCH] No channel or oauth token was provided.')
    cmpc.send_webhook(config['discord']['systemlog'], 'FAILED TO START - No Oauth or username was provided.')
    sys.exit(2)

if not PANEL_API_KEY:
    log.warning('[CHATBOT] No api key was provided to the panel, command has been disabled.')

# Misc final setup
mouse = Controller()
processor = cmpc.CommandProcessor(config, 'executing.txt', mouse)
processor.log_to_obs(None)
# TODO: remove
# t = TwitchPlays_Connection.Twitch()
# t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN)


# This is a bit of a hack, we should make cmpc.CommandProcessor.log_to_obs more flexible instead
def custom_log_to_obs(log_string, message_object, command_processor=processor):
    """Write a custom message to the obs log file.

    Args:
        log_string -- the string to log to the file
        message_object -- the original cmpc.TwitchMessage message which invoked the command
        command_processor -- the cmpc.CommandProcessor to use to log to obs
    Does not return
    """
    message_edited = copy.copy(message_object)
    message_edited.original_content = log_string
    command_processor.log_to_obs(message_edited)


def handle_new_messages(timestamp, tags, channel, user, message):
    written_nothing = True

    # TODO: remove
    # # Get all messages from Twitch
    # new_messages = t.twitch_receive_messages()
    #
    # # If we didn't get any new messages, let's log that nothing is happening and
    # # keep looping for new stuff
    # if not new_messages:
    #     if written_nothing:
    #         processor.log_to_obs(None)
    #         written_nothing = False
    #     continue
    #
    # # We got some messages, nice! In that case, let's loop through each and try and process it
    # for message in new_messages:

    # Move the payload into an object so we can make better use of it
    # noinspection PyTypeChecker
    # TODO: also refactor cmpc.TwitchMessage to handle the new message format. This is a hack
    message_dict = {
        'message': message,
        'username': user,
    }

    twitch_message = cmpc.TwitchMessage(message_dict)

    # Command processing is very scary business - let's wrap the whole thing in a try/catch
    # NO, BAD
    # read an error handling guide
    # TODO - remove
    try:
        # Log the chat if that's something we want to do
        if config['options']['LOG_ALL']:
            log.info(f'CHAT LOG: {twitch_message.get_log_string()}')
        if config['options']['LOG_PPR']:
            with open('chat.log', 'a', encoding='utf-8') as f:
                f.write(f'{twitch_message.get_log_string()}\n')

        # Process this beef
        command_has_run = processor.process_commands(twitch_message)
        if command_has_run:
            written_nothing = False
            return
        user_permissions = USER_PERMISSIONS.get(twitch_message.username, cmpc.Permissions())

        # Commands for authorised developers in dev list only.
        if user_permissions.script or user_permissions.developer:
            if twitch_message.content == 'script- testconn':
                cmpc.send_webhook(config['discord']['modtalk'],
                                  'Connection made between twitch->script->webhook->discord')

            if twitch_message.content == 'script- reqdata':
                context = {
                    'user': twitch_message.username,
                    'channel': TWITCH_USERNAME,
                    'modlist': [i for i, o in USER_PERMISSIONS.items() if o.moderator],
                    'devlist': [i for i, o in USER_PERMISSIONS.items() if o.developer],
                    'options': config['options'],
                }
                cmpc.send_data(config['discord']['modtalk'], context)

            if twitch_message.content == 'script- apirefresh':
                apiconfig = requests.get(config['api']['apiconfig'])
                apiconfig = json.loads(apiconfig.text)
                # Note - all caps variables should really be constants.
                USER_PERMISSIONS = load_user_permissions(
                    dev_list=apiconfig['devlist'],
                    mod_list=apiconfig['modlist'],
                )
                log.info('[API] refreshed')
                cmpc.send_webhook(config['discord']['systemlog'], 'API was refreshed.')

            if twitch_message.content == 'script- forceerror':
                cmpc.send_error(config['discord']['systemlog'], 'Forced error!',
                                twitch_message, TWITCH_USERNAME,
                                config['options']['DEPLOY'], branch_name, branch_name_assumed)

            if twitch_message.original_content.startswith('chatbot- '):
                if not PANEL_API_KEY:
                    log.error('[CHATBOT] Command ran and no API key, '
                              'skipping command and sending warning to discord.')
                    cmpc.send_webhook(config['discord']['systemlog'],
                                      'No chatbot api key was provided, skipping command.')
                    return
                # IF YOU NEED AN API KEY, CONTACT MAX.
                signal = processor.remove_prefix(twitch_message.original_content, 'chatbot- ')
                payload = {
                    "signal": signal
                }
                headers = {
                    'User-Agent': f'{USER_AGENT}',
                    'Accept': 'application/json',
                    # DO NOT REMOVE THE QUOTES HERE.
                    'Authorization': f'Bearer {PANEL_API_KEY}',
                }
                try:
                    x = requests.post(config['api']['panelapiendpoint'], json=payload, headers=headers)
                    cmpc.send_webhook(config['discord']['systemlog'],
                                      f'Chatbot control ran({signal}) and returned with a code of {x.status_code}')
                except requests.RequestException:
                    log.error(f'Could not execute chatbot control: {twitch_message.original_content}',
                              sys.exc_info())

        # Commands for authorized moderators in mod list only.
        if user_permissions.script or user_permissions.developer or user_permissions.moderator:
            if twitch_message.content.startswith('modsay '):
                data = {
                    'username': twitch_message.username,
                    'content': processor.remove_prefix(twitch_message.original_content, 'modsay '),
                }
                try:
                    result = requests.post(config['discord']['modtalk'],
                                           json=data, headers={'User-Agent': USER_AGENT})
                except requests.RequestException:
                    log.error(f"Could not modsay this moderator's message: {twitch_message.original_content}",
                              sys.exc_info())

            if twitch_message.content in ['hideall']:
                pyautogui.hotkey('win', 'm')
            if twitch_message.content in ['mute']:
                pyautogui.press('volumemute')

            if twitch_message.content in ['el muchacho']:
                # pyautogui.hotkey('win', 'r')
                # pyautogui.typewrite('vlc -f --no-repeat --no-osd --no-play-and-pause '
                #                     '"https://www.youtube.com/watch?v=GdtuG-j9Xog" vlc://quit')
                # pyautogui.typewrite('https://www.youtube.com/watch?v=GdtuG-j9Xog')
                # pyautogui.press('enter')
                webbrowser.open('https://www.youtube.com/watch?v=GdtuG-j9Xog', new=1)

            if twitch_message.content.startswith('script- suspend '):
                duration = processor.remove_prefix(twitch_message.content, 'script- suspend ')
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
                        custom_log_to_obs(log_message, twitch_message)
                        time.sleep(duration)
                    except ValueError:
                        log.error(f'Could not suspend for duration: {twitch_message.content}\nDue to negative arg')
                    except OverflowError:
                        log.error(f'Could not suspend for duration: {twitch_message.content}\n'
                                  'Due to too large arg')

            if twitch_message.content.startswith('!defcon '):
                severity = processor.remove_prefix(twitch_message.content, '!defcon ')

                if severity == '1':
                    pyautogui.hotkey('win', 'm')
                    pyautogui.press('volumemute')
                    # pyautogui.hotkey('win', 'r')
                    # pyautogui.typewrite('shutdown -s -t 0 -c "!defcon 1 -- emergency shutdown" -f -d u:5:19')
                    # pyautogui.press('enter')
                    os.system('shutdown -s -t 0 -c "!defcon 1 -- emergency shutdown" -f -d u:5:19')
                    custom_log_to_obs('[defcon 1, EMERGENCY SHUTDOWN]', twitch_message)
                    time.sleep(999999)
                # TODO: Add !defcon 2 -- close all running programs
                elif severity == '3':
                    pyautogui.hotkey('win', 'm')
                    pyautogui.press('volumemute')
                    custom_log_to_obs('[defcon 3, suspend script]', twitch_message)
                    time.sleep(86400)
                elif severity == 'blue':
                    # pyautogui.hotkey('win', 'r')
                    # pyautogui.typewrite('vlc -f --repeat --no-osd --no-play-and-pause '
                    #                     '"https://www.youtube.com/watch?v=GdtuG-j9Xog"')
                    # pyautogui.typewrite('https://www.youtube.com/watch?v=GdtuG-j9Xog')
                    # pyautogui.press('enter')
                    webbrowser.open('https://www.youtube.com/watch?v=GdtuG-j9Xog', new=1)
                    custom_log_to_obs('[defcon BLUE, el muchacho de los ojos tristes]', twitch_message)
                    time.sleep(30)

        # Commands for cmpcscript only.
        if user_permissions.script:
            print(f'CMPC SCRIPT: {twitch_message.content}')
            if twitch_message.original_content == 'c3RyZWFtc3RvcGNvbW1hbmQxMjYxMmYzYjJmbDIzYmFGMzRud1Qy':
                sys.exit(1)

    except Exception as error:
        # Send error data to systemlog.
        log.error(f'{error}', sys.exc_info())
        cmpc.send_error(config['discord']['systemlog'], error,
                        twitch_message, TWITCH_USERNAME,
                        config['options']['DEPLOY'], branch_name, branch_name_assumed)


if __name__ == '__main__':
    twitch_client = cmpc.TwitchConnection(TWITCH_USERNAME,
                                          processor.remove_prefix(TWITCH_OAUTH_TOKEN, 'oauth:')).start()
    twitch_client.on_message = handle_new_messages
    twitch_client.handle_forever()
