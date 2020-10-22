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

# Stock Python imports
import time
import subprocess
import ctypes
import random
import string
import re
import sys
import json
import os

# PyPI dependency imports.
import requests
import pyautogui
import pynput

from pynput.mouse import Button, Controller

# File imports.
import cmpc
import TwitchPlays_Connection

from TwitchPlays_AccountInfo import *


# Send starting up message with webhook if in config.
if START_MSG == 'true':
    cmpc.send_webhook(systemlog, 'script online')

# Get dev and mod lists from API.
print('[API] Requsting data!')
devsr = requests.get(DEV_API)
modsr = requests.get(MOD_API)
MODS = modsr.text
DEVS = devsr.text
print('[API] Data here, and parsed!')

# File management

# Remove temp chat log or log if it doesn't exist.
if os.path.exists('chat.log'):
  os.remove('chat.log')
else:
    print('[LOG] does not exist')
    
currentexec = open('executing.txt', 'w')

# Function to write the default status to OBS file if no commands in progress.
def nothing():
    currentexec.truncate()
    currentexec.write('nothing')

# Connect to Twitch API.  
t = TwitchPlays_Connection.Twitch()
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN)



# Mainloop
while True:
    new_messages = t.twitch_recieve_messages()
    # If new messages list is empty, write default status to OBS and continue
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

                # Log new message if in config.
                if LOG_ALL == 'true':
                    print('CHAT LOG: ' + usr + ': ' + msg)
                if LOG_PPR == 'true':
                    f = open('chat.log', 'a')
                    f.write(usr + ':' + msg)
                    f.write('\n')
                    f.close()

            # Function to write the currently executing command to OBS.
            def obs():
                currentexec.seek(0,0)
                currentexec.write(msg_preserve_caps + ' (' + usr + ')')
                time.sleep(0.5)
                
                print(msg_preserve_caps + ' (' + usr + ')')

                # Send command info to chatrelay webhook.
                t = time.localtime()
                current_time = time.strftime('%H:%M:%S', t)
                current_time_modded = 'Time: ' + current_time
                
                data = {'embeds': [],
                        'username': usr,
                        'content': current_time_modded}
                
                embed = {'description': msg_preserve_caps,
                         'title': 'Command event:'}
                data['embeds'].append(embed)
                
                result = requests.post(chatrelay, data=json.dumps(data),
                                       headers={'Content-Type': 'application/json'})

            # Co-ordinate data for mosue move commands.
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
                ('far left'): (-300, 0),
                ('far right'): (300, 0),
                ('far up'): (0, -300),
                ('far down'): (0, 300),
            }

            # Aliases to pyautogui key codes for keypress commands.
            press_key_data = {
                ('tab',): ('tab'),
                ('enter'): ('enter'),
                ('windows key', 'win'): ('win'),
                ('backspace', 'back space', 'delete'): ('backspace'),
                ('space', 'spacebar'): ('space'),
                ('page up', 'pageup'): ('pageup'),
                ('page down', 'pagedown'): ('pagedown'),
                ('esc', 'escape'): ('esc'),
                ('arrow down'): ('down'),
                ('arrow up'): ('up'),
                ('arrow left'): ('left'),
                ('arrow right'): ('right'),
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

            # Compare command with aliases in each dict.
            # This replaces a large if statement chain.
            for key, value in keycode_compare_data.items():
                if msg in key: # keycode_compare_data
                    cmpc.move(*value)
                    obs()
            for key, ktp in press_key_data.items():
                if msg in key: # press_key_data
                    pyautogui.press(ktp)
                    obs()
            for key, btp in click_data.items():
                if msg in key: # press_key_data
                    if key == 'doubleclick':
                        times = 2
                    else: 
                        times = 1
                    pyautogui.click(button=btp, clicks=times)
                    obs()

            # Other regular commands
            if msg in ['center']:
                obs()
                xval,yval = tuple(res/2 for res in pyautogui.size())
                pyautogui.moveTo(xval,yval)
            if msg in ['control t', 'ctrl t', 'new tab']:
                obs()
                pyautogui.hotkey('ctrl', 'n')
            if msg in ['control s', 'ctrl s', 'save']:
                obs()
                pyautogui.hotkey('ctrl', 's')
            if msg in ['control z', 'undo']:
                obs()
                pyautogui.hotkey('ctrl', 'z')
            if msg in ['alt tab', 'alt-tab']:
                obs()
                pyautogui.hotkey('altleft', 'tab')
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
                pyautogui.drag(-50, 0, 0.25, button='left')
            if msg in ['copy', 'control c']:
                obs()
                pyautogui.hotkey('ctrl', 'c')
            if msg in ['paste', 'control v']:
                obs()
                pyautogui.hotkey('ctrl', 'v')
            if msg in ['its stuck', 'it is stuck']:
                obs()
                mouse.position = (500, 500)
            if msg in ['close tab', 'close the tab']:
                obs()
                pyautogui.hotkey('ctrl', 'w')
            if msg in ['screenshot', 'screen shot']:
                obs()
                pyautogui.hotkey('win', 'prtsc')
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

            # Command to send alert in discord that a mod is needed.
            if msg in ['!modalert']:
                # Log and send to chatalert webhook.
                print('(MA) called.')
                
                data = {'embeds': [],
                        'username': usr,
                        'content': '<@&741308237135216650> '\
                                   'https://twitch.tv/controlmypc'}

                embed = {'title': ':rotating_light: '\
                                  '**The user above needs a moderator '\
                                  'on the stream.** '\
                                  ':rotating_light:'}
                data['embeds'].append(embed)

                print('(MA) Sending request...')
                result = requests.post(chatalerts, data=json.dumps(data),
                                       headers={'Content-Type': 'application/json'})
                print('(MA) Request sent')

            # Commands for cmpcscript only.
            if usr == 'cmpcscript':
                # Log
                print('CMPC SCRIPT')
                print(msg)

                # Stop the script if message matches this key.
                if msg_preserve_caps == 'c3RyZWFtc3RvcGNvbW1hbmQxMjYxMmYzYjJmbDIzYmFGMzRud1Qy':
                    break

            # Commands for authorised developers in dev list only.
            if usr in DEVS:
                if msg == 'script- testconn':
                    cmpc.send_webhook(modtalk, 'Connection made between twitch->script->webhook->discord')
                if msg == 'script- reqdata':
                    optionsstr = f'Log All: {LOG_ALL}\nStart Message: {START_MSG}\nEXC_MSG: {EXC_MSG}\nLog PPR: {LOG_PPR}'
                    context = {'options': optionsstr,
                               'user': usr,
                               'devlist': DEVS,
                               'modlist': MODS,
                               'channel': TWITCH_USERNAME}

                    cmpc.senddata(modtalk, context)
                if msg == 'script- apirefresh':
                    devsr = requests.get(DEV_API)
                    modsr = requests.get(MOD_API)
                    MODS = modsr.text
                    DEVS = devsr.text
                    print('API Refreshed!')
                    cmpc.send_webhook(modtalk, 'API was refreshed.')
                if msg == 'script- forceerror':
                    cmpc.send_error(systemlog, 'Forced error!', msg, usr, TWITCH_USERNAME)
                # TODO: remove duplicated modsay code
                if msg.startswith('modsay '): 
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {'username': usr,
                                'content': typeMsg}
                        
                        result = requests.post(modtalk, data=json.dumps(data),
                                               headers={'Content-Type': 'application/json'})
                    except:
                        print('Could not modsay this moderators message!' + msg)

            # Commands for moderators in mod list only.
            if usr in MODS:
                # Command to send message to modtalk webhook.
                if msg.startswith('modsay '): 
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {'username': usr,
                                'content': typeMsg}

                        result = requests.post(modtalk, data=json.dumps(data),
                                               headers={'Content-Type': 'application/json'})
                    except:
                        print('Could not modsay this moderators message!' + msg)

            # Commands for big man controlmypc only.
            if usr == 'controlmypc':
                if msg == 'starting soon':
                    obs()
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(S, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
                if msg == 'main':
                    obs()
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(C, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
                if msg == 'stop the stream!':
                    obs()
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(Q, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
                if msg == 'maintenance':
                    obs()
                    PressKeyPynput(LEFT_ALT)   
                    PressAndHoldKey(M, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)

            # Regular commands that take arguments.
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

            # More regular commands I guess
            if msg in ['select all', 'ctrl a', 'control a']:
                    obs()
                    PressKeyPynput(LEFT_CONTROL)
                    PressAndHoldKey(A, 0.1)
                    ReleaseKeyPynput(LEFT_CONTROL)
            if msg in ['tayne', 'ctrl k', 'control k']:
                    obs()
                    PressKeyPynput(LEFT_CONTROL)
                    PressAndHoldKey(K, 0.1)
                    ReleaseKeyPynput(LEFT_CONTROL)
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

            if msg in ['scroll down']:
                obs()
                for scrl in range(5):
                    pyautogui.scroll(-60)
            if msg in ['scroll up']:
                obs()
                for scrl in range(5):
                    pyautogui.scroll(60)
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
            # Ok there's no order to this atm
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
                    
        except Exception as error:
            # Send error data to systemlog.
            print(f'[ERROR]: {error}')
            cmpc.send_error(systemlog, error, msg, usr, TWITCH_USERNAME)

