# Stock Python imports
import os  # file manager

# PyPI dependency imports.
import requests  # api and discord webhooks
import toml  # configuration
from pynput.mouse import Controller

# File imports.
import cmpc  # Utility local Package
import TwitchPlays_Connection


# Log copyright notice.
COPYRIGHT_NOTICE = """
------------------------------------------
           TWITCH PLAYS
           REWRITE BRANCH
           https://cmpc.live
           © 2020 controlmypc
           by CMPC Developers & Kae
------------------------------------------
"""
print(COPYRIGHT_NOTICE)


# Load Configuration
config = toml.load('config.toml')
TWITCH_USERNAME = config['twitch']['channel']
TWITCH_OAUTH_TOKEN = config['twitch']['oauth_token']
USERAGENT = config['api']['useragent']
mouse = Controller()


# Send starting up message with webhook if in config.
if config['options']['START_MSG']:
    cmpc.send_webhook(config['discord']['systemlog'], 'Script Online')


USER_PERMISSIONS = {}
def load_user_permissions(dev_list, mod_list):
    global USER_PERMISSIONS
    USER_PERMISSIONS.clear()
    for user in dev_list:
        perms = USER_PERMISSIONS.get(user, cmpc.Permissions())
        perms.developer = True
        USER_PERMISSIONS[user] = perms
    for user in mod_list:
        perms = USER_PERMISSIONS.get(user, cmpc.Permissions())
        perms.moderator = True
        USER_PERMISSIONS[user] = perms
    USER_PERMISSIONS.setdefault('cmpcscript', cmpc.Permissions()).script = True


# Get dev and mod lists from API.
# print('[API] Requesting data!')
# dev_sr = requests.get(config['api']['mod'], headers={'User-Agent': USERAGENT})
# mod_sr = requests.get(config['api']['dev'], headers={'User-Agent': USERAGENT})
load_user_permissions(
    dev_list=['maxlovetoby'],
    mod_list=['maxlovetoby'],
)
print('[API] Data here, and parsed!')


# Remove temp chat log or log if it doesn't exist.
if os.path.exists('chat.log'):
    os.remove('chat.log')
else:
    print('[LOG] does not exist')


if not TWITCH_USERNAME or not TWITCH_OAUTH_TOKEN:
    print('[TWITCH] No channel or oauth token was provided.')
    cmpc.send_webhook(config['discord']['systemlog'], 'FAILED TO START - No Oauth or username was provided.')
    exit(2)


currentexec = open('executing.txt', 'w')
processor = cmpc.CommandProcessor(config, currentexec, mouse)
t = TwitchPlays_Connection.Twitch()
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN)


# Main loop
while True:

    # Get all messages from Twitch
    new_messages = t.twitch_recieve_messages()

    # If we didn't get any new messages, let's log that nothing is happening and
    # keep looping for new stuff
    if not new_messages:
        processor.log_to_obs(None)
        continue

    # We got some messages, nice! In that case, let's loop through each and try and process it
    for message in new_messages:

        # Command processing is very scary business - let's wrap the whole thing in a try/catch
        try:

            # Move the payload into an object so we can make better use of it
            twitch_message = cmpc.TwitchMessage(message)

            # Log the chat if that's something we want to do
            if config['options']['LOG_ALL']:
                print(f'CHAT LOG: {twitch_message.get_log_string()}')
            if config['options']['LOG_PPR']:
                with open('chat.log', 'a') as f:
                    f.write(f"{twitch_message.get_log_string()}\n")

            # Process this beef
            command_has_run = processor.process_commands(message)
            if command_has_run:
                continue
            user_permissions = USER_PERMISSIONS.get(twitch_message.username, cmpc.Permissions())

            # Commands for authorised developers in dev list only.
            if user_permissions.script or user_permissions.developer:
                if twitch_message.content == 'script- testconn':
                    cmpc.send_webhook(config['discord']['modtalk'], 'Connection made between twitch->script->webhook->discord')
                    context = {
                        'options': 'optionsstr',
                        'user': twitch_message.username,
                        'devlist': [i for i, o in USER_PERMISSIONS.items() if o.developer],
                        'modlist': [i for i, o in USER_PERMISSIONS.items() if o.moderator],
                        'channel': TWITCH_USERNAME,
                    }
                    cmpc.send_data(config['discord']['modtalk'], context)

                if twitch_message.content == 'script- apirefresh':
                    dev_sr = requests.get(config['api']['dev'])
                    mod_sr = requests.get(config['api']['mod'])
                    load_user_permissions(
                        dev_list=dev_sr.json(),
                        mod_list=mod_sr.json(),
                    )
                    print('[API] refresheed')
                    cmpc.send_webhook(config['discord']['systemlog'], 'API was refreshed.')

                if twitch_message.content == 'script- forceerror':
                    cmpc.send_error(config['discord']['systemlog'], 'Forced error!', twitch_message.content, twitch_message.username, TWITCH_USERNAME)

            # Commands for authorized moderators in mod list only.
            if user_permissions.script or user_permissions.developer or user_permissions.moderator:
                if twitch_message.content.startswith('modsay '):
                    try:
                        data = {
                            'username': twitch_message.username,
                            'content': twitch_message.original_content[7:],
                        }
                        result = requests.post(config['discord']['modtalk'], json=data, headers={'User-Agent': USERAGENT})
                    except Exception:
                        print('Could not modsay this moderators message: ' + twitch_message.content)

            # Commands for cmpcscript only.
            if user_permissions.script:
                print(f'CMPC SCRIPT: {twitch_message.content}')
                if twitch_message.original_content == 'c3RyZWFtc3RvcGNvbW1hbmQxMjYxMmYzYjJmbDIzYmFGMzRud1Qy':
                    exit(1)

        except Exception as error:
            # Send error data to systemlog.
            print(f'[ERROR]: {error}')
            cmpc.send_error(config['discord']['systemlog'], error, twitch_message.content, twitch_message.username, TWITCH_USERNAME)
