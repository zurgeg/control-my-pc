import requests
import time
import sys
import pyautogui
if sys.platform == "darwin":
    pass
else:
    import pydirectinput
import json
def get_platform():
    platform = sys.platform
    return platform
def directorauto():
    platform = get_platform()
    if platform == "darwin":
        return('auto')
    else:
        return('direct')
def send_webhook(url, content):
    data = {}
    data["content"] = content
    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
def send_error(url, error, msg, usr):
    data = {}
    data["embeds"] = []
    error = str(error)
    embed = {}
    embed["description"] = msg
    embed["title"] = error
    data["username"] = usr
    data["content"] = "A exception was encountered while reading twitch chat, information is contained in this message/embed/username."
    data["embeds"].append(embed)    
    result = requests.post(url, data=json.dumps(data), headers={"Content-Type": "application/json"})
def move(*args):
    dor = directorauto()
    if dor == "auto":
        pyautogui.move(*args)
    if dor == "direct":
        pydirectinput.move(*args)
def press(key):
    pyautogui.press(key)    

