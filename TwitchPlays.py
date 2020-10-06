import time
import os
import json
import ctypes

import pyautogui
import pydirectinput
import requests
import pynput
from pynput.mouse import Button, Controller

import TwitchPlays_Connection
from TwitchPlays_AccountInfo import (
    TWITCH_USERNAME, TWITCH_OAUTH_TOKEN, LOG_ALL, START_MSG, EXC_MSG, LOG_PPR,
    chatalerts, chatrelay, modtalk, botstat, DEV_API, MOD_API,
)
from keycodes import KeyboardKeycodes


print("------------------------------------------")
print("           TWITCH PLAYS                   ")
print("           MASTER BRANCH                  ")
print("           https://cmpc.live              ")
print("           © 2020-2020 fadedmax           ")
print("           By fadedmax, with cmpc devs.   ")
print("------------------------------------------")
print("[API] Requsting data!")

devsr = requests.get(DEV_API)
modsr = requests.get(MOD_API)
MODS = modsr.text
DEVS = devsr.text
print("[API] Data here, and parsed!")


# <--Webhook-->
if START_MSG == "true":
    data = {}
    data["content"] = "script running"
    result = requests.post(botstat, data=json.dumps(data), headers={"Content-Type": "application/json"})
    print("[DISCORD] Start webhook message sent!")


# <--File mgmt-->
if os.path.exists("chat.log"):
    os.remove("chat.log")
else:
    print('[LOG] does not exist')


text_file = open("executing.txt", "w")
SendInput = ctypes.windll.user32.SendInput


def nothing():
    open("executing.txt", "w")
    text_file.seek(0,0)
    text_file.write("nothing")


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


def press_and_release_key(key_code):
    PressKeyPynput(key_code)
    ReleaseKeyPynput(key_code)


def exctwitchchat(username, message):
    data = {
        "embeds": [
            {
                "description": message,
                "title": "Execption:",
            }
        ],
        "username": username,
        "content": "A exception was encountered while reading twitch chat, information is contained in this message/embed/username.",
    }
    requests.post(chatrelay, data=json.dumps(data), headers={"Content-Type": "application/json"})


def obs(file, username, message):
    file.seek(0,0)
    file.write(f"{message} ({username})")
    time.sleep(0.5)
    print(f"{message} ({username})")
    data = {
        "username": username,
        "content": "Time: " + time.strftime("%H:%M:%S", time.localtime()),
        "embeds": [
            {
                "description": message,
                "title": "Command event:",
            }
        ],
    }
    requests.post(chatrelay, data=json.dumps(data), headers={"Content-Type": "application/json"})


# DirectX codes are found at: https://docs.microsoft.com/en-us/previous-versions/visualstudio/visual-studio-6.0/aa299374(v=vs.60)
mouse = Controller()


t = TwitchPlays_Connection.Twitch()
t.twitch_connect(TWITCH_USERNAME, TWITCH_OAUTH_TOKEN)


while True:

    new_messages = t.twitch_recieve_messages()
    if not new_messages:
        nothing()
        continue

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

            keycode_compare_data = {
                ('left',): (-100,0),
                ('light left', 'little left',): (-25,0),
                ('super light left', 'super little left',): (-10, 0),
                ('right',): (100,0),
                ('light right', 'little right',): (25,0),
                ('super light right', 'super little right',): (10, 0),
                ('up',): (0, -100),
                ('light up', 'little up',): (0, -25),
                ('super light up', 'super little up',): (0, -10),
                ('down',): (0, 100),
            }
            for key, value in keycode_compare_data.items():
                if msg in key:
                    obs(text_file, usr, msg_preserve_caps)
                    pydirectinput.move(*value)

            if msg in ['light down', 'little down']:
                obs(text_file, usr, msg_preserve_caps)
                pydirectinput.move(0, 25)

            if msg in ['super light down', 'super little down']:
                obs(text_file, usr, msg_preserve_caps)
                pydirectinput.move(0, 10)

            if msg in ['center']:
                obs(text_file, usr, msg_preserve_caps)
                xval,yval = tuple(res / 2 for res in pyautogui.size())
                pydirectinput.moveTo(xval,yval)

            if msg in ['rightclick', 'right click']:
                obs(text_file, usr, msg_preserve_caps)
                mouse.press(Button.right)
                time.sleep(0.1)
                mouse.release(Button.right)

            if msg in ['click']:
                obs(text_file, usr, msg_preserve_caps)
                mouse.press(Button.left)
                time.sleep(0.1)
                mouse.release(Button.left)

            if msg in ['doubleclick', 'double click']:
                obs(text_file, usr, msg_preserve_caps)
                mouse.press(Button.left)
                time.sleep(0.1)
                mouse.release(Button.left)
                mouse.press(Button.left)
                time.sleep(0.1)
                mouse.release(Button.left)

            keycode_compare_data = {
                ('tab',): KeyboardKeycodes.TAB,
                ('enter',): KeyboardKeycodes.ENTER,
                ('space', 'spacebar',): KeyboardKeycodes.SPACE,
                ('where?', 'where',): KeyboardKeycodes.LEFT_CONTROL,
                ('win', 'windows key', 'win key',): KeyboardKeycodes.L_WIN,
            }
            for key, value in keycode_compare_data.items():
                if msg in key:
                    obs(text_file, usr, msg_preserve_caps)
                    press_and_release_key(value)

            if msg in ['control t', 'ctrl t', 'new tab']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.RIGHT_CONTROL)
                time.sleep(0.1)
                PressKeyPynput(KeyboardKeycodes.T)
                ReleaseKeyPynput(KeyboardKeycodes.RIGHT_CONTROL)
                ReleaseKeyPynput(KeyboardKeycodes.T)

            if msg in ['control w', 'ctrl w', 'close tab']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.RIGHT_CONTROL)
                time.sleep(0.1)
                PressKeyPynput(KeyboardKeycodes.W)
                ReleaseKeyPynput(KeyboardKeycodes.RIGHT_CONTROL)
                ReleaseKeyPynput(KeyboardKeycodes.W)

            if msg in ['control s', 'ctrl s', 'save']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.RIGHT_CONTROL)
                time.sleep(0.1)
                PressKeyPynput(KeyboardKeycodes.S)
                ReleaseKeyPynput(KeyboardKeycodes.RIGHT_CONTROL)
                ReleaseKeyPynput(KeyboardKeycodes.S)

            if msg in ['drag mouse up']:
                obs(text_file, usr, msg_preserve_caps)
                pyautogui.drag(0, -50, 0.25, button='left')

            if msg in ['drag mouse down']:
                obs(text_file, usr, msg_preserve_caps)
                pyautogui.drag(0, 50, 0.25, button='left')

            if msg in ['drag mouse right']:
                obs(text_file, usr, msg_preserve_caps)
                pyautogui.drag(50, 0, 0.25, button='left')

            if msg in ['drag mouse left']:
                pyautogui.drag(-50, 0, 0.25, button='left')

            if msg in ['backspace', 'back space', 'delete']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.BACKSPACE)
                time.sleep(0.1)
                ReleaseKeyPynput(KeyboardKeycodes.BACKSPACE)

            if msg in ['arrow up', 'up arrow']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.UP_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(KeyboardKeycodes.UP_ARROW)

            if msg in ['arrow down', 'down arrow']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.DOWN_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(KeyboardKeycodes.DOWN_ARROW)

            if msg in ['arrow left', 'left arrow']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.LEFT_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(KeyboardKeycodes.LEFT_ARROW)

            if msg in ['arrow right', 'right arrow']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.RIGHT_ARROW)
                time.sleep(1)
                ReleaseKeyPynput(KeyboardKeycodes.RIGHT_ARROW)

            if msg in ['quit']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.LEFT_ALT)
                PressAndHoldKey(KeyboardKeycodes.Ffour, 0.1)
                ReleaseKeyPynput(KeyboardKeycodes.LEFT_ALT)

            if msg in ['refresh', 'F5']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.LEFT_ALT)
                PressAndHoldKey(KeyboardKeycodes.Ffive, 0.1)
                ReleaseKeyPynput(KeyboardKeycodes.LEFT_ALT)

            if msg in ['its stuck', 'it is stuck']:
                obs(text_file, usr, msg_preserve_caps)
                mouse.position = (500, 500)

            if msg in ['escape', 'esc']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.ESC)
                ReleaseKeyPynput(KeyboardKeycodes.ESC)

            if msg in ['page up']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.PAGE_UP)
                ReleaseKeyPynput(KeyboardKeycodes.PAGE_UP)

            if msg in ['page down']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.PAGE_DOWN)
                ReleaseKeyPynput(KeyboardKeycodes.PAGE_DOWN)

            if msg in ['close tab', 'close the tab']:
                obs(text_file, usr, msg_preserve_caps)
                PressKeyPynput(KeyboardKeycodes.LEFT_CONTROL)
                PressAndHoldKey(KeyboardKeycodes.W, 0.1)
                ReleaseKeyPynput(KeyboardKeycodes.LEFT_CONTROL)

            if msg in ['hold mouse', 'hold the mouse']:
                obs(text_file, usr, msg_preserve_caps)
                mouse.press(Button.left)
                time.sleep(3)
                mouse.release(Button.left)

            if msg == "hold mouse long":
                obs(text_file, usr, msg_preserve_caps)
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
                    except Exception:
                        print("Could not modsay this moderators message!" + msg)

            if usr in MODS:

                if msg.startswith("modsay "):
                    try:
                        typeMsg = msg_preserve_caps[7:]
                        data = {}
                        data["content"] = typeMsg
                        data["username"] = usr
                        result = requests.post(modtalk, data=json.dumps(data), headers={"Content-Type": "application/json"})
                    except Exception:
                        print("Could not modsay this moderators message!" + msg)

            if usr == "controlmypc":

                if msg == "starting soon":

                    obs(text_file, usr, msg_preserve_caps)
                    PressKeyPynput(KeyboardKeycodes.LEFT_ALT)
                    PressAndHoldKey(KeyboardKeycodes.S, 0.1)
                    ReleaseKeyPynput(KeyboardKeycodes.LEFT_ALT)

                if msg == "main":
                    obs(text_file, usr, msg_preserve_caps)
                    PressKeyPynput(KeyboardKeycodes.LEFT_ALT)
                    PressAndHoldKey(KeyboardKeycodes.C, 0.1)
                    ReleaseKeyPynput(KeyboardKeycodes.LEFT_ALT)

                if msg == "stop the stream!":
                    obs(text_file, usr, msg_preserve_caps)
                    PressKeyPynput(KeyboardKeycodes.LEFT_ALT)
                    PressAndHoldKey(KeyboardKeycodes.Q, 0.1)
                    ReleaseKeyPynput(KeyboardKeycodes.LEFT_ALT)

                if msg == "maintenance":
                    obs(text_file, usr, msg_preserve_caps)
                    PressKeyPynput(KeyboardKeycodes.LEFT_ALT)
                    PressAndHoldKey(KeyboardKeycodes.M, 0.1)
                    ReleaseKeyPynput(KeyboardKeycodes.LEFT_ALT)

            if msg.startswith("type "):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    typeMsg = msg_preserve_caps[5:]
                    pyautogui.typewrite(typeMsg)
                except Exception:
                    print("COULD NOT TYPE: " + msg)

            if msg.startswith("press "):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    typeMsg = msg_preserve_caps[5:]
                    pyautogui.typewrite(typeMsg)
                except Exception:
                    print("COULD NOT TYPE: " + msg)

            if msg.startswith("gtype "):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    typeMsg = msg[6:]
                    pydirectinput.typewrite(typeMsg)
                except Exception:
                    print("COULD NOT TYPE: " + msg)

            if msg in ['select all', 'ctrl a', 'control a']:
                    obs(text_file, usr, msg_preserve_caps)
                    PressKeyPynput(KeyboardKeycodes.LEFT_CONTROL)
                    PressAndHoldKey(KeyboardKeycodes.A, 0.1)
                    ReleaseKeyPynput(KeyboardKeycodes.LEFT_CONTROL)

            if msg in ['tayne', 'ctrl k', 'control k']:
                    obs(text_file, usr, msg_preserve_caps)
                    PressKeyPynput(KeyboardKeycodes.LEFT_CONTROL)
                    PressAndHoldKey(KeyboardKeycodes.K, 0.1)
                    ReleaseKeyPynput(KeyboardKeycodes.LEFT_CONTROL)

            if msg.startswith("go to "):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    coord = msg[6:]
                    if coord == "center":
                        xval,yval = tuple(res / 2 for res in pyautogui.size())
                    else:
                        xval,yval = coord.split(' ',1)
                    xval = int(xval)
                    yval = int(yval)
                    pydirectinput.moveTo(xval, yval)
                except Exception:
                    print("could not go to somehow: " + msg)

            if msg.startswith("drag to "):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    mouse.press(Button.left)
                    coord = msg[8:]
                    if coord == "center":
                        xval,yval = tuple(res / 2 for res in pyautogui.size())
                    else:
                        xval,yval = coord.split(' ',1)
                    xval = int(xval)
                    yval = int(yval)
                    pydirectinput.moveTo(xval, yval)
                    mouse.release(Button.left)
                except Exception:
                    print("could not drag to cuz: " + msg)

            if msg.startswith('d for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[6:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.D, timee)
                except Exception:
                    print('error')
            if msg.startswith('a for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[6:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.A, timee)
                except Exception:
                    print('error')
            if msg.startswith('s for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[6:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.S, timee)
                except Exception:
                    print('error')
            if msg.startswith('w for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[6:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.W, timee)
                except Exception:
                    print('error')
            if msg.startswith('arrow up for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[13:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.UP_ARROW, timee)
                except Exception:
                    print('er')
            if msg.startswith('arrow left for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[15:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.LEFT_ARROW, timee)
                except Exception:
                    print('er')
            if msg.startswith('arrow right for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[16:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.RIGHT_ARROW, timee)
                except Exception:
                    print('er')
            if msg.startswith('arrow down for '):
                try:
                    obs(text_file, usr, msg_preserve_caps)
                    timee = msg[15:]
                    timee = float(timee)
                    if timee <= 10 and timee >= 0:
                        PressAndHoldKey(KeyboardKeycodes.DOWN_ARROW, timee)
                except Exception:
                    print('er')

    except Exception:
        print('EXCEPTION HAPPENED')
        if EXC_MSG == "true":
            exctwitchchat()
