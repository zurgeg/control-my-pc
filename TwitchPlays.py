print("------------------------------------------");
print("           TWITCH PLAYS         ");
print("           MASTER BRANCH         ")
print("           https://cmpc.live     ");
print("           © 2020-2020 fadedmax");
print("           By fadedmax, with cmpc devs.");
print("------------------------------------------");
import TwitchPlays_Connection
import time
import subprocess
import ctypes
import random
import string
import re
import sys
import os
import pyautogui
#import pydirectinput
import requests
import pynput
import json
from TwitchPlays_AccountInfo import TWITCH_USERNAME, TWITCH_OAUTH_TOKEN, LOG_ALL, START_MSG, EXC_MSG, LOG_PPR
from TwitchPlays_AccountInfo import chatalerts, chatrelay, modtalk, botstat, DEV_API, MOD_API
from pynput.mouse import Button, Controller
print("[API] Requsting data!")
devsr = requests.get(DEV_API)
modsr = requests.get(MOD_API)
MODS = modsr.text
DEVS = devsr.text
print("[API] Data here, and parsed!")
#<--Webhook-->
if START_MSG == "true":
    data = {}
    data["content"] = "script running"
    result = requests.post(botstat, data=json.dumps(data), headers={"Content-Type": "application/json"})
    print("[DISCORD] Start webhook message sent!")
#<--File mgmt-->
if os.path.exists("chat.log"):
  os.remove("chat.log")
else:
    print('[LOG] does not exist')
text_file = open("executing.txt", "w")
#SendInput = ctypes.windll.user32.SendInput
def nothing():
    open("executing.txt", "w")
    text_file.seek(0,0)
    n = text_file.write("nothing")
def PressKeyPynput(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
def ReleaseKeyPynput(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = pynput._util.win32.INPUT_union()
    ii_.ki = pynput._util.win32.KEYBDINPUT(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.cast(ctypes.pointer(extra), ctypes.c_void_p))
    x = pynput._util.win32.INPUT(ctypes.c_ulong(1), ii_)
    SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
def PressAndHoldKey(hexKeyCode, seconds):
    PressKeyPynput(hexKeyCode)
    time.sleep(seconds)
    ReleaseKeyPynput(hexKeyCode)
def exctwitchchat():
            data = {}
            data["embeds"] = []
            embed = {}
            embed["description"] = msg
            embed["title"] = "Exception:"
            data["username"] = usr
            data["content"] = "A exception was encountered while reading twitch chat, information is contained in this message/embed/username."
            data["embeds"].append(embed)    
            result = requests.post(chatrelay, data=json.dumps(data), headers={"Content-Type": "application/json"})
#DirectX codes are found at:https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa299374(v=vs.60)
mouse = Controller()
Q=0x10
W=0x11
E=0x12
R=0x13
T=0x14
Y=0x15
U=0x16
I=0x17
O=0x18
P=0x19
A=0x1E
S=0x1F
D=0x20
F=0x21
G=0x22
H=0x23
J=0x24
K=0x25
L=0x26
Z=0x2C
X=0x2D
C=0x2E
V=0x2F
B=0x30
N=0x31
M=0x32
ESC=0x01
ONE=0x02
TWO=0x03
THREE=0x04
FOUR=0x05
FIVE=0x06
SIX=0x07
SEVEN=0x08
EIGHT=0x09
NINE=0x0A
ZERO=0x0B
MINUS=0x0C
EQUALS=0x0D
BACKSPACE=0x0E
SEMICOLON=0x27
TAB=0x0F
CAPS=0x3A
ENTER=0x1C
LEFT_CONTROL=0x1D
LEFT_ALT=0x38
LEFT_SHIFT=0x2A
SPACE=0x39
DELETE=0x53
COMMA=0x33
PERIOD=0x34
BACKSLASH=0x35
NUMPAD_0=0x52
NUMPAD_1=0x4F
NUMPAD_2=0x50
NUMPAD_3=0x51
NUMPAD_4=0x4B
NUMPAD_5=0x4C
NUMPAD_6=0x4D
NUMPAD_7=0x47
NUMPAD_8=0x48
NUMPAD_9=0x49
NUMPAD_PLUS=0x4E
NUMPAD_MINUS=0x4A
LEFT_ARROW=0xCB
RIGHT_ARROW=0xCD
UP_ARROW=0xC8
DOWN_ARROW=0xD0
LEFT_MOUSE=0x100
RIGHT_MOUSE=0x101
MIDDLE_MOUSE=0x102
MOUSE3=0x103
MOUSE4=0x104
MOUSE5=0x105
MOUSE6=0x106
MOUSE7=0x107
MOUSE_WHEEL_UP=0x108
MOUSE_WHEEL_DOWN=0x109
Ffour=0x3E
Ffive=0x3F
RIGHT_SHIFT=0x36
RIGHT_CONTROL=0xA3
RIGHT_ALT=0xA5
L_WIN=0x5B
R_WIN=0x5C
t = TwitchPlays_Connection.Twitch();
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN);
while True:
    new_messages = t.twitch_recieve_messages();
    if not new_messages:
        nothing()
        continue
    else:

        try:
            for message in new_messages:
                msg = message['message'].lower()
                msg_preserve_caps = message['message']
                username = message['username'].lower()
                usr = username.decode()
                if LOG_ALL == "true":
                    print('CHAT LOG: ' + usr + ': ' + msg)
                if LOG_PPR == "true":
                    f = open("chat.log", "a")
                    f.write(usr + ':' + msg)
                    f.write("\n")
                    f.close()
            def obs():
                text_file.seek(0,0)
                text_file.write(msg_preserve_caps + " (" + usr + ")")
                time.sleep(0.5)
                print (msg_preserve_caps + ' (' + usr + ')')
                t = time.localtime()
                current_time = time.strftime("%H:%M:%S", t)
                current_time_modded = "Time: " + current_time
                data = {}
                data["embeds"] = []
                embed = {}
                embed["description"] = msg_preserve_caps
                embed["title"] = "Command event:"
                data["username"] = usr
                data["content"] = current_time_modded
                data["embeds"].append(embed)    
                result = requests.post(chatrelay, data=json.dumps(data), headers={"Content-Type": "application/json"})
                
            if msg in ['left']:
                obs()
                pydirectinput.move(-100,0)
            if msg in ['light left', 'little left']:
                obs()
                pydirectinput.move(-25,0)
            if msg in ['super light left', 'super little left']:
                obs()
                pydirectinput.move(-10, 0)
            if msg in ['right']:
                obs()
                pydirectinput.move(100,0)
            if msg in ['light right', 'little right']:
                obs()
                pydirectinput.move(25,0)
            if msg in ['super light right', 'super little right']:
                obs()
                pydirectinput.move(10, 0)
            if msg in ['up']:
                obs()
                pydirectinput.move(0, -100)
            if msg in ['light up', 'little up']:
                obs()
                pydirectinput.move(0, -25)
            if msg in ['super light up', 'super little up']:
                obs()
                pydirectinput.move(0, -10)
            if msg in ['down']:
                obs()
                pydirectinput.move(0, 100)
            if msg in ['light down', 'little down']:
                obs()
                pydirectinput.move(0, 25) 
            if msg in ['super light down', 'super little down']:
                obs()
                pydirectinput.move(0, 10)

            if msg in ['rightclick', 'right click']:
                obs()
                mouse.press(Button.right)
                time.sleep(0.1)
                mouse.release(Button.right)
            if msg in ['click']:
                obs()
                mouse.press(Button.left)
                time.sleep(0.1)
                mouse.release(Button.left)
            if msg in ['doubleclick', 'double click']:
                obs()
                mouse.press(Button.left)
                time.sleep(0.1)
                mouse.release(Button.left)
                mouse.press(Button.left)
                time.sleep(0.1)
                mouse.release(Button.left)
            if msg in ['tab']:
                obs()
                PressKeyPynput(TAB)
                ReleaseKeyPynput(TAB)
            if msg in ['enter']:
                obs()
                PressKeyPynput(ENTER)
                ReleaseKeyPynput(ENTER)
            if msg in ['space', 'spacebar']:
                obs()
                PressKeyPynput(SPACE)
                ReleaseKeyPynput(SPACE)
            if msg in ['where?', 'where']:
                obs()
                PressKeyPynput(LEFT_CONTROL)
                ReleaseKeyPynput(LEFT_CONTROL)
            if msg in ['win', 'windows key', 'win key']:
                obs()
                PressKeyPynput(L_WIN)
                ReleaseKeyPynput(L_WIN)
            """if msg in ['stop all keys', 'stop keys', '!stop', '!end', 'end keys', 'end all keys', 'release key', 'release keys', 'release all keys']:
                obs()
                ReleaseKeyPynput(RIGHT_CONTROL)
                ReleaseKeyPynput(RIGHT_ALT)
                ReleaseKeyPynput(TAB)
                ReleaseKeyPynput(LEFT_SHIFT)   
            if msg in ['hold ctrl', 'hold control', 'hold ctrl key', 'hold control key']:
                obs()
                PressKeyPynput(RIGHT_CONTROL)
            if msg in ['hold alt', 'hold alt key']:
                obs()
                PressKeyPynput(RIGHT_ALT)
            if msg in ['hold tab', 'hold tab key']:
                obs()
                PressKeyPynput(TAB)
            if msg in ['hold shift', 'hold shift key']:
                obs()
                PressKeyPynput(LEFT_SHIFT)
"""
            if msg in ['control t', 'ctrl t', 'new tab']:
                obs()
                PressKeyPynput(RIGHT_CONTROL)
                time.sleep(0.1)
                PressKeyPynput(T)
                ReleaseKeyPynput(RIGHT_CONTROL)
                ReleaseKeyPynput(T)
            if msg in ['control w', 'ctrl w', 'close tab']:
                obs()
                PressKeyPynput(RIGHT_CONTROL)
                time.sleep(0.1)
                PressKeyPynput(W)
                ReleaseKeyPynput(RIGHT_CONTROL)
                ReleaseKeyPynput(W)
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
            if msg in ['backspace', 'back space', 'delete']:
                obs()
                PressKeyPynput(BACKSPACE)
                time.sleep(0.1)
                ReleaseKeyPynput(BACKSPACE)
            if msg in ['arrow up', 'up arrow']:
                obs()
                PressKeyPynput(UP_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(UP_ARROW)
            if msg in ['arrow down', 'down arrow']:
                obs()
                PressKeyPynput(DOWN_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(DOWN_ARROW)
            if msg in ['arrow left', 'left arrow']:
                obs()
                PressKeyPynput(LEFT_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(LEFT_ARROW)
            if msg in ['arrow right', 'right arrow']:
                obs()
                PressKeyPynput(RIGHT_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(RIGHT_ARROW)
            if msg in ['quit']:
                obs()
                PressKeyPynput(LEFT_ALT)
                PressAndHoldKey(Ffour, 0.1)
                ReleaseKeyPynput(LEFT_ALT)
            if msg in ['refresh', 'F5']:
                obs()
                PressKeyPynput(LEFT_ALT)
                PressAndHoldKey(Ffive, 0.1)
                ReleaseKeyPynput(LEFT_ALT)
            if msg in ['its stuck', 'it is stuck']:
                obs()
                mouse.position = (500, 500)
            if msg in ['escape', 'esc']:
                obs()
                PressKeyPynput(ESC)
                ReleaseKeyPynput(ESC)
            if msg in ['close tab', 'close the tab']:
                obs()
                PressKeyPynput(LEFT_CONTROL)
                PressAndHoldKey(W, 0.1)
                ReleaseKeyPynput(LEFT_CONTROL)
            if msg in ['hold mouse', 'hold the mouse']:
                obs()
                mouse.press(Button.left)
                time.sleep(3)
                mouse.release(Button.left)
            if msg == "hold mouse long":
                obs()
                mouse.press(Button.left)
                time.sleep(9)
                mouse.release(Button.left)
            if msg in ['!modalert']:
                print("(MA) called.")
                data["username"] = usr
                data = {}
                data["embeds"] = []
                embed = {}  
                embed["title"] = ":rotating_light: **The user above needs a moderator on the stream.** :rotating_light:"
                data["username"] = usr
                data["embeds"].append(embed)
                data["content"] = "<@&741308237135216650> https://twitch.tv/controlmypc"
                print("(MA) Sending request...")
                result = requests.post(chatalerts, data=json.dumps(data), headers={"Content-Type": "application/json"})
                print("(MA) Request sent")

            if usr == "cmpcscript":
                print("CMPC SCRIPT")
                print(msg)
                if msg_preserve_caps == "c3RyZWFtc3RvcGNvbW1hbmQxMjYxMmYzYjJmbDIzYmFGMzRud1Qy":
                    break       
            if usr in DEVS:
                if msg == "script- testconn":
                    data = {}
                    data["content"] = "Connection made between twitch->script->webhook->discord"
                    result = requests.post(modtalk, data=json.dumps(data), headers={"Content-Type": "application/json"})
                if msg == "script- reqdata":
                    data = {}
                    data["content"] = "Data Requested from twitch! **LOG_ALL** " + LOG_ALL + " **START_MSG** " + START_MSG + " **EXC_MSG** " + EXC_MSG + " **LOG_PPR** " + LOG_PPR + " **MODS** " + str(MODS) + " **DEVS** " + str(DEVS) + " **CHANNEL** " + str(TWITCH_USERNAME) 
                    result = requests.post(modtalk, data=json.dumps(data), headers={"Content-Type": "application/json"})
                if msg.startswith("modsay "): 
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {}
                        data["content"] = typeMsg
                        data["username"] = usr
                        result = requests.post(modtalk, data=json.dumps(data), headers={"Content-Type": "application/json"})
                    except:
                        print("Could not modsay this moderators message!" + msg)

            if usr in MODS:
                if msg.startswith("modsay "): 
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {}
                        data["content"] = typeMsg
                        data["username"] = usr
                        result = requests.post(modtalk, data=json.dumps(data), headers={"Content-Type": "application/json"})
                    except:
                        print("Could not modsay this moderators message!" + msg)
                

            if usr == "controlmypc":
                if msg == "starting soon":
                    obs()
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(S, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
                if msg == "main":
                    obs()
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(C, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
                if msg == "stop the stream!":
                    obs()
                    PressKeyPynput(LEFT_ALT)
                    PressAndHoldKey(Q, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
                if msg == "maintenance":
                    obs()
                    PressKeyPynput(LEFT_ALT)   
                    PressAndHoldKey(M, 0.1)
                    ReleaseKeyPynput(LEFT_ALT)
            if msg.startswith("type "): 
                try:
                    obs()
                    typeMsg = msg_preserve_caps[5:]
                    pyautogui.typewrite(typeMsg)
                except:
                    print("COULD NOT TYPE: " + msg)
            if msg.startswith("gtype "): 
                try:
                    obs()
                    typeMsg = msg[6:]
                    pydirectinput.typewrite(typeMsg)
                except:
                    print("COULD NOT TYPE: " + msg)

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
            if msg.startswith("go to "):
                try:
                    obs()
                    coord = msg[6:]
                    xval,yval = coord.split(' ',1)
                    xval = int(xval)
                    yval = int(yval)
                    pydirectinput.moveTo(xval, yval) 
                except:
                    print("could not go to somehow: " + msg)

            if msg.startswith("drag to "):
                try:
                    obs()
                    mouse.press(Button.left)
                    coord = msg[8:]
                    xval,yval = coord.split(' ',1)
                    xval = int(xval)
                    yval = int(yval)
                    pydirectinput.moveTo(xval, yval)
                    mouse.release(Button.left) 
                except:
                    print("could not drag to cuz: " + msg)

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
            
        except:
            print('EXCEPTION HAPPENED')
            if EXC_MSG == "true":
                exctwitchchat()
