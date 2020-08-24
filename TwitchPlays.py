print("MASTER BRANCH - this code is stable. If not contact other devs.")
import time
import subprocess
import ctypes
import random
import string
import re
import sys
import TwitchPlays_Connection
import pyautogui
#import pydirectinput
import requests
from TwitchPlays_AccountInfo import TWITCH_USERNAME, TWITCH_OAUTH_TOKEN
import pynput
import json
from pynput.mouse import Button, Controller
chatalerts = "https://discordapp.com/api/webhooks/741306005589327952/RMDc8zdyYG1BNuLjL2EDUIYVNwCJoJgwld8G8czXEwnp9kv_oGLMmv77RG5AoubrgfW8"
chatrelay = "https://discordapp.com/api/webhooks/741316193369194506/slrRQYiTHPP6uNPeIflzIBuw6SQ5cZnsd_E6YHvl6BowBp-BPEVRl_cj0pN3TpYcxPcl"
modtalk = "https://discordapp.com/api/webhooks/741311244308578392/7azdTbjAljUT0PTjBkTJzddh4i4vTj1H-_A1zJJVMZEYOIGWsP_1e60vTIJK-PQTOhEk"
botstat = "https://discordapp.com/api/webhooks/741343798285697126/_XYbtaaGAyRb5rgJMqNuph6DcHHxfMs7Ast12wDUZt1EWwfdsCbszem_ZuM79WWSlQsT"
#<--Webhook-->
data = {}
data["content"] = "script running"
result = requests.post(botstat, data=json.dumps(data), headers={"Content-Type": "application/json"})
print("(max) - start message sent")
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
            if msg in ['light left']:
                obs()
                pydirectinput.move(-25,0)
            if msg in ['super light left']:
                obs()
                pydirectinput.move(-10, 0)
            if msg in ['right']:
                obs()
                pydirectinput.move(100,0)
            if msg in ['light right']:
                obs()
                pydirectinput.move(25,0)
            if msg in ['super light right']:
                obs()
                pydirectinput.move(10, 0)
            if msg in ['up']:
                obs()
                pydirectinput.move(0, -100)
            if msg in ['light up']:
                obs()
                pydirectinput.move(0, -25)
            if msg in ['super light up']:
                obs()
                pydirectinput.move(0, -10)
            if msg in ['down']:
                obs()
                pydirectinput.move(0, 100)
            if msg in ['light down']:
                obs()
                pydirectinput.move(0, 25) 
            if msg in ['super light down']:
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
            if msg in ['stop all keys', 'stop keys', '!stop', '!end', 'end keys', 'end all keys', 'release key', 'release keys', 'release all keys']:
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
            if msg in ['control T', 'ctrl T']:
                obs()
                PressKeyPynput(RIGHT_CONTROL)
                time.sleep(0.1)
                PressKeyPynput(T)
                ReleaseKeyPynput(RIGHT_CONTROL)
                ReleaseKeyPynput(T)
            if msg in ['control W', 'ctrl W']:
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
                    print("Typing this particular message didn't work: " + msg)
            if msg in ['select all', 'ctrl a', 'control a']:
                    obs()
                    PressKeyPynput(LEFT_CONTROL)
                    PressAndHoldKey(A, 0.1)
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
                    print("Typing this particular message didn't work: " + msg)
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
                    if timee<=10:
                        PressAndHoldKey(LEFT_ARROW,timee)
                except:
                    print('er')    
            if msg.startswith('arrow right for '): 
                try:
                    obs()
                    timee = msg[16:]
                    timee = float(timee)
                    if timee<=10 and time>=0:
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
            print('Encountered an exception while reading chat.')
            exctwitchchat() #dont delete this line, only put a # in front of it to disable the webhook (discord) messages.

