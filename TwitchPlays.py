# Log copyright notice.
print("""\
------------------------------------------
           TWITCH PLAYS                   
           REWRITE BRANCH                 
           https://cmpc.live              
           © 2020 controlmypc             
           by CMPC Developers             
------------------------------------------
""")
print('[SYSTEM] Importing')
# Stock Python imports
import time # for sleeping
import ctypes
import string
import re
import sys # system utilitys
import json # helper with requests
import os # file manager

# PyPI dependency imports.
import requests # api and discord webhooks 
import pyautogui # main keyboard controller and mouse movement
import pynput # utilitys
import toml # configuration
from pynput.mouse import Button, Controller

# File imports.
import cmpc # Utility local Package
import TwitchPlays_Connection
print('[SYSTEM] Imported everything, starting startup proccess.')

# Load Configuration
config = toml.load('config.toml')
TWITCH_USERNAME = config['twitch']['channel']
TWITCH_OAUTH_TOKEN = config['twitch']['oauth_token']
USERAGENT = config['api']['useragent']
t = TwitchPlays_Connection.Twitch()

# Send starting up message with webhook if in config.
if config['options']['START_MSG'] == 'true':
    cmpc.send_webhook(config['discord']['systemlog'], 'Script Online')

# Get dev and mod lists from API.
print('[API] Requsting data!')
devsr = requests.get(config['api']['mod'], headers={'User-Agent': USERAGENT})
modsr = requests.get(config['api']['dev'], headers={'User-Agent': USERAGENT})
MODS = modsr.text
DEVS = devsr.text
print('[API] Data here, and parsed!')

# Remove temp chat log or log if it doesn't exist.
if os.path.exists('chat.log'):
  os.remove('chat.log')
else:
    print('[LOG] does not exist')

# Open file that OBS reads from for displaying the currently executing command.
currentexec = open('executing.txt', 'w')


# Function to write the default status to OBS file if no commands in progress.
def nothing():
    currentexec.truncate()
    currentexec.write('nothing')

# Function to write the currently executing command to OBS and logging.
def obs():
    currentexec.truncate()
    currentexec.write(msg_preserve_caps + ' (' + usr + ')')
    time.sleep(0.5)
    
    print(msg_preserve_caps + ' (' + usr + ')')

    # Send command info to chatrelay webhook.
    lt = time.localtime()
    current_time = time.strftime('%H:%M:%S', lt)
    current_time_modded = 'Time: ' + current_time
    
    data = {'embeds': [],
            'username': usr,
            'content': current_time_modded}
    
    embed = {'description': msg_preserve_caps,
             'title': 'Command event:'}
    data['embeds'].append(embed)
    
    result = requests.post(config['discord']['chatrelay'], data=json.dumps(data),
                           headers={'Content-Type': 'application/json', 'User-Agent': USERAGENT})



# Check if twitch login config is ok.
if not TWITCH_USERNAME or not TWITCH_OAUTH_TOKEN:
    print('[TWITCH] No channel or oauth token was provided.')
    cmpc.send_webhook(config['discord']['systemlog'], 'FAILED TO START- No Oauth or username was provided.')
    exit(2)

# Connect to Twitch IRC
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN)


# Mainloop
while True:
    new_messages = t.twitch_recieve_messages()
    # If new messages list is empty, write default status to OBS and continue checking nfor new messages
    if not new_messages:
        nothing()
        continue
    else:
        try:
            for message in new_messages:
                # Get message data.
                msg = message['message'].lower()
                msg_preserve_caps = message['message']
                username = message['username'].lower()
                usr = username.decode()
                config['options']
                # Log new message if in config.
                if config['options']['LOG_ALL'] == 'true':
                    print('CHAT LOG: ' + usr + ': ' + msg)
                if config['options']['LOG_PPR'] == 'true':
                    f = open('chat.log', 'a')
                    f.write(usr + ':' + msg)
                    f.write('\n')
                    f.close()

            # Aliases to pyautogui key codes for keypress commands.
            #TODO: fix pageup and arrow commands to not fuck up everything.
            press_key_data = {
                ('enter'): ('enter'),
                ('tab',): ('tab'),
                ('esc', 'escape'): ('esc'),
                ('windows key', 'win'): ('win'),
                ('backspace', 'back space', 'delete'): ('backspace'),
                ('space', 'spacebar'): ('space'),
                #('page up', 'pageup'): ('pageup'),
                #('page down', 'pagedown'): ('pagedown'),
                #('arrow down'): ('down'),
                #('arrow up'): ('up'),
                #('arrow left'): ('left'),
                #('arrow right'): ('right'),
                ('refresh', 'F5'): ('f5'),
                ('where', 'where?'): ('ctrl'),
            }

            # Aliases to pyautogui key codes for clicking commands.
            click_data = {
                ('click', 'left click'): ('left'),
                ('doubleclick', 'double click'): ('doubleclick'),
                ('rightclick', 'right click'): ('right'),
                ('middleclick', 'middle click'): ('middle'),
            }
            
            # Co-ordinate data for mouse move commands.
            keycode_compare_data = {
                ('left',): (-100, 0),
                ('light left', 'little left',): (-25, 0),
                ('super light left', 'super little left',): (-10, 0),
                ('right',): (100, 0),
                ('light right', 'little right',): (25, 0),
                ('super light right', 'super little right',): (10, 0),
                ('up',): (0, -100),
                ('light up', 'little up',): (0, -25),
                ('super light up', 'super little up',): (0, -10),
                ('down',): (0, 100),    
            }

            # Compare command with aliases in each dict.
            # This replaces a large if statement chain.
            for key, ktp in press_key_data.items():
                if msg in key: # press_key_data
                    pyautogui.press(ktp)
                    obs()
            for key, btp in click_data.items():
                if msg in key: # click_data
                    if key == 'doubleclick':
                        times = 2
                    else: 
                        times = 1
                    pyautogui.click(button=btp, clicks=times)
                    obs()
            for key, value in keycode_compare_data.items():
                if msg in key: # keycode_compare_data
                    cmpc.move(*value)
                    obs()

            # Control Shourtcuts
            if msg in ['control t', 'ctrl t', 'new tab']:
                obs()
                pyautogui.hotkey('ctrl', 'n')
            if msg in ['control s', 'ctrl s', 'save']:
                obs()
                pyautogui.hotkey('ctrl', 's')
            if msg in ['control z', 'undo']:
                obs()
                pyautogui.hotkey('ctrl', 'z')
            if msg in ['control c', 'copy']:
                obs()
                pyautogui.hotkey('ctrl', 'c')
            if msg in ['control v', 'paste']:
                obs()
                pyautogui.hotkey('ctrl', 'v')
            if msg in ['control w', 'close tab', 'close the tab']:
                obs()
                pyautogui.hotkey('ctrl', 'w')
            if msg in ['control a', 'select all', 'ctrl a']:
                obs()
                pyautogui.hotkey('ctrl', 'a')
            if msg in ['control k', 'tayne', 'ctrl k']:
                obs()
                pyautogui.hotkey('ctrl', 'k')

            # Misc Commands
            if msg in ['quit', 'alt f4']:
                obs()
                pyautogui.hotkey('altleft', 'f4')
            if msg in ['alt tab', 'alt-tab']:
                obs()
                pyautogui.hotkey('altleft', 'tab')
            if msg in ['screenshot', 'screen shot']:
                obs()
                pyautogui.hotkey('win', 'prtsc')
            # Mouse
            if msg in ['hold mouse', 'hold the mouse']:
                obs()
                mouse.press(Button.left)
                time.sleep(3)
                mouse.release(Button.left)
            if msg in ['hold mouse long']:
                obs()
                mouse.press(Button.left)
                time.sleep(9)
                mouse.release(Button.left)
            if msg in ['scroll down']:
                obs()
                for scrl in range(5):
                    pyautogui.scroll(-60)
            if msg in ['scroll up']:
                obs()
                for scrl in range(5):
                    pyautogui.scroll(60)
            if msg in ['drag mouse up']:
                obs()
                pyautogui.drag(0, -50, 0.25, button='left')
            if msg in ['drag mouse down']:
                obs()
                pyautogui.drag(0, 50, 0.25, button='left')
            if msg in ['drag mouse right']:
                obs()
                pyautogui.drag(50, 0, 0.25, button='left')
            if msg in ['drag mouse left']:
                obs()
                pyautogui.drag(-50, 0, 0.25, button='left')
            if msg in ['center']:
                obs()
                xval,yval = tuple(res/2 for res in pyautogui.size())
                pyautogui.moveTo(xval,yval)
            if msg in ['its stuck', 'it is stuck']:
                obs()
                mouse.position = (500, 500)


            # Command to send alert in discord that a mod is needed.
            if msg in ['!modalert']:
                # Log and send to chatalert webhook.
                print('[MODALERT] called.')
                
                data = {'embeds': [],
                        'username': usr,
                        'content': '<@&741308237135216650> '\
                                   'https://twitch.tv/controlmypc',
                }

                embed = {'title': ':rotating_light: '\
                                  '**The user above needs a moderator '\
                                  'on the stream.** '\
                                  ':rotating_light:',
                }
                data['embeds'].append(embed)

                print('[MODALERT] Sending request...')
                result = requests.post(config['discord']['chatalerts'], data=json.dumps(data),
                                       headers={'Content-Type': 'application/json', 'User-Agent': USERAGENT})
                print('[MODALERT] Request sent')

            # Regular commands that take arguments.
            # PyAutoGUI commands with arguments
            if msg.startswith('type '): 
                try:
                    obs()
                    typeMsg = msg_preserve_caps[5:]
                    pyautogui.typewrite(typeMsg)
                except:
                    print('COULD NOT TYPE: ' + msg)
            if msg.startswith('press '): 
                try:
                    obs()
                    typeMsg = msg_preserve_caps[5:]
                    pyautogui.typewrite(typeMsg)
                except:
                    print('COULD NOT TYPE: ' + msg)
                    
            if msg.startswith('scroll up for '):
                try:
                    scrll = msg[14:]
                    scrll = int(scrll)
                    if scrll<=20 and scrll>=0:
                        obs()
                        for scrl in range(scrll):
                            pyautogui.scroll(1)
                except:
                    print('error')
            if msg.startswith('scroll down for '):
                try:
                    scrll = msg[16:]
                    scrll = int(scrll)
                    if scrll<=20 and scrll>=0:
                        obs()
                        for scrl in range(scrll):
                            pyautogui.scroll(-1)
                except:
                    print('error')
            if msg.startswith('go to '):
                try:
                    obs()
                    coord = msg[6:]
                    if coord == 'center':
                        xval,yval = tuple(res/2 for res in pyautogui.size())
                    else:
                        xval,yval = coord.split(' ',1)
                    xval = int(xval)
                    yval = int(yval)
                    pyautogui.moveTo(xval, yval) 
                except:
                    print('could not go to somehow: ' + msg)

            # pynput commands with arguments
            #TODO: replace press and hold key with a pyautogui style thing
            if msg.startswith('d for '): 
                try:
                    obs()
                    timee = msg[6:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(D,timee)
                except:
                    print('error')
            if msg.startswith('a for '): 
                try:
                    obs()
                    timee = msg[6:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(A,timee)
                except:
                    print('error')
            if msg.startswith('s for '): 
                try:
                    obs()
                    timee = msg[6:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(S,timee)
                except:
                    print('error')
            if msg.startswith('w for '): 
                try:
                    obs()
                    timee = msg[6:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(W,timee)
                except:
                    print('error')
            if msg.startswith('arrow up for '): 
                try:
                    obs()
                    timee = msg[13:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(UP_ARROW,timee)
                except:
                    print('er')   
            if msg.startswith('arrow left for '): 
                try:
                    obs()
                    timee = msg[15:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(LEFT_ARROW,timee)
                except:
                    print('er')
            if msg.startswith('arrow right for '): 
                try:
                    obs()
                    timee = msg[16:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(RIGHT_ARROW,timee)
                except:
                    print('er')
            if msg.startswith('arrow down for '): 
                try:
                    obs()   
                    timee = msg[15:]
                    timee = float(timee)
                    if timee<=10 and timee>=0:
                        PressAndHoldKey(DOWN_ARROW,timee)
                except:
                    print('er')


            # Commands that are exclusive to certain users

            # Commands for authorised developers in dev list only.
            if usr in DEVS:
                if msg == 'script- testconn':
                    cmpc.send_webhook(config['discord']['modtalk'], 'Connection made between twitch->script->webhook->discord')
                #TODO: get this to fucking work with the new config
                #if msg == 'script- reqdata':
                    #optionsstr = str('Disabled.')
                    context = {'options': """optionsstr""",
                               'user': usr,
                               'devlist': DEVS,
                               'modlist': MODS,
                               'channel': TWITCH_USERNAME,
                    }

                    cmpc.senddata(config['discord']['modtalk'], context)
                if msg == 'script- apirefresh':
                    devsr = requests.get(DEV_API)
                    modsr = requests.get(MOD_API)
                    MODS = modsr.text
                    DEVS = devsr.text
                    print('[API] refresheed')
                    cmpc.send_webhook(systemlog, 'API was refreshed.')
                if msg == 'script- forceerror':
                    cmpc.send_error(systemlog, 'Forced error!', msg, usr, TWITCH_USERNAME)
                # TODO: remove duplicated modsay code
                # Command to send message to modtalk webhook.
                if msg.startswith('modsay '): 
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {'username': usr,
                                'content': typeMsg,
                        }
                        
                        result = requests.post(config['discord']['modtalk'], data=json.dumps(data),
                                               headers={'Content-Type': 'application/json', 'User-Agent': USERAGENT})
                    except:
                        print('Could not modsay this moderators message!' + msg)

            # Commands for authorized moderators in mod list only.
            if usr in MODS:
                # Command to send message to modtalk webhook.
                if msg.startswith('modsay '): 
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {'username': usr,
                                'content': typeMsg,
                        }
                        #TODO: replace this with cmpc package.
                        result = requests.post(config['discord']['modtalk'], data=json.dumps(data),
                                               headers={'Content-Type': 'application/json', 'User-Agent': USERAGENT})
                    except:
                        print('Could not modsay this moderators message: ' + msg)

            # Commands for cmpcscript only.
            if usr == 'cmpcscript':
                # Log
                print(f'CMPC SCRIPT: {msg}')
                # Stop the script if message matches this key.
                if msg_preserve_caps == 'c3RyZWFtc3RvcGNvbW1hbmQxMjYxMmYzYjJmbDIzYmFGMzRud1Qy':
                    break
                    exit(1)

        except Exception as error:
            # Send error data to systemlog.
            print(f'[ERROR]: {error}')
            cmpc.send_error(config['discord']['systemlog'], error, msg, usr, TWITCH_USERNAME)

currentexec.close()
