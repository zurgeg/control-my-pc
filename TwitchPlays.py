# PSL Packages;
import os  # file manager and .env handler
import json  # json, duh,
import logging as log  # better print()

# PIP Packages;
import pyautogui  # only used in rawsend- command
import requests  # api and discord webhooks
import toml  # configuration
from pynput.mouse import Controller  # Not really needed, but (i think) something still relies on it so /shrug

# Local Packages;
import cmpc  # Pretty much all of the custom shit we need.
import TwitchPlays_Connection  # Connect to twitch via IRC.


# Log copyright notice.
COPYRIGHT_NOTICE = """
------------------------------------------
           TWITCH PLAYS
           STAGING BRANCH
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
        log.FileHandler('system.log'),
        log.StreamHandler()
    ]
)
# Load Configuration
log.debug('Stand by me.')
config = toml.load('config.toml')
USERAGENT = config['api']['useragent']
mouse = Controller()
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


# Send starting up message with webhook if in config.
if config['options']['START_MSG']:
    cmpc.send_webhook(config['discord']['systemlog'], 'Script Online')


USER_PERMISSIONS = {}


def load_user_permissions(dev_list, mod_list):
    global USER_PERMISSIONS
    USER_PERMISSIONS.clear()
    for dev in dev_list:
        perms = USER_PERMISSIONS.get(dev, cmpc.Permissions())
        perms.developer = True
        USER_PERMISSIONS[dev] = perms
    for mod in mod_list:
        perms = USER_PERMISSIONS.get(mod, cmpc.Permissions())
        perms.moderator = True
        USER_PERMISSIONS[mod] = perms
    USER_PERMISSIONS.setdefault('cmpcscript', cmpc.Permissions()).script = True


# Get dev and mod lists from API.
log.info('[API] Requesting data!')
apiconfig = requests.get(config['api']['apiconfig'])
apiconfig = json.loads(apiconfig.text)

load_user_permissions(
    dev_list=apiconfig['devlist'],
    mod_list=apiconfig['modlist'],
)
log.info('[API] Data here, and parsed!')


# Remove temp chat log or log if it doesn't exist.
if os.path.exists('chat.log'):
    os.remove('chat.log')
else:
    pass

if not TWITCH_USERNAME or not TWITCH_OAUTH_TOKEN:
    log.fatal('[TWITCH] No channel or oauth token was provided.')
    cmpc.send_webhook(config['discord']['systemlog'], 'FAILED TO START - No Oauth or username was provided.')
    exit(2)


currentexec = open('executing.txt', 'w')
processor = cmpc.CommandProcessor(config, currentexec, mouse)
processor.log_to_obs(None)
t = TwitchPlays_Connection.Twitch()
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN)


# Main loop
while True:
    written_nothing = True

    # Get all messages from Twitch
    new_messages = t.twitch_receive_messages()

    # If we didn't get any new messages, let's log that nothing is happening and
    # keep looping for new stuff
    if not new_messages:
        if written_nothing:
            processor.log_to_obs(None)
            written_nothing = False
        continue

    # We got some messages, nice! In that case, let's loop through each and try and process it
    for message in new_messages:

        # Command processing is very scary business - let's wrap the whole thing in a try/catch
        try:

            # Move the payload into an object so we can make better use of it
            # noinspection PyTypeChecker
            twitch_message = cmpc.TwitchMessage(message)

            # Log the chat if that's something we want to do
            if config['options']['LOG_ALL']:
                log.info(f'CHAT LOG: {twitch_message.get_log_string()}')
            if config['options']['LOG_PPR']:
                with open('chat.log', 'a') as f:
                    f.write(f'{twitch_message.get_log_string()}\n')

            # Process this beef
            command_has_run = processor.process_commands(twitch_message)
            if command_has_run:
                written_nothing = False
                continue
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
                    dev_sr = requests.get(config['api']['dev'])
                    mod_sr = requests.get(config['api']['mod'])
                    load_user_permissions(
                        dev_list=dev_sr.json(),
                        mod_list=mod_sr.json(),
                    )
                    log.info('[API] refresheed')
                    cmpc.send_webhook(config['discord']['systemlog'], 'API was refreshed.')

                if twitch_message.content == 'script- forceerror':
                    cmpc.send_error(config['discord']['systemlog'], 'Forced error!',
                                    twitch_message.content, twitch_message.username, TWITCH_USERNAME)

                if twitch_message.original_content.startswith('rawsend- '):
                    try:
                        keytopress = twitch_message.original_content[9:]
                        pyautogui.press(keytopress)
                    except Exception as error:
                        log.warning('Could not rawtype: ' + twitch_message.content)
                        cmpc.send_error(config['discord']['systemlog'], error,
                                        twitch_message.content, twitch_message.username, TWITCH_USERNAME)

            # Commands for authorized moderators in mod list only.
            if user_permissions.script or user_permissions.developer or user_permissions.moderator:
                if twitch_message.content.startswith('modsay '):
                    try:
                        data = {
                            'username': twitch_message.username,
                            'content': twitch_message.original_content[7:],
                        }
                        result = requests.post(config['discord']['modtalk'],
                                               json=data, headers={'User-Agent': USERAGENT})
                    except Exception:
                        log.warning('Could not modsay this moderators message: ' + twitch_message.content)

            # Commands for cmpcscript only.
            if user_permissions.script:
                print(f'CMPC SCRIPT: {twitch_message.content}')
                if twitch_message.original_content == 'c3RyZWFtc3RvcGNvbW1hbmQxMjYxMmYzYjJmbDIzYmFGMzRud1Qy':
                    exit(1)

        except Exception as error:
            # Send error data to systemlog.
            log.error(f'[ERROR]: {error}')
            cmpc.send_error(config['discord']['systemlog'], error,
                            twitch_message.content, twitch_message.username, TWITCH_USERNAME)
