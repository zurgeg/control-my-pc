import requests
import time
import sys
import pyautogui
import psutil
if sys.platform == "darwin":
    pass
else:
    import pydirectinput
import json
def get_platform():
    platform = sys.platform
    return platform
def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
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
def send_error(url, error, msg, usr, channel):
    datatest = {"embeds": [{"title": "Script - Exception Occured","description": f"***Last Sent Message -*** {msg}\n\n***Exception Info -*** {error}\n\n[***Stream Link***](https://twitch.tv/{channel})","color": 1107600,"footer": {"text": 'User: ' + usr + ' - Channel: ' + channel,"icon_url": "https://blog.twitch.tv/assets/uploads/generic-email-header-1.jpg"}}]}
    result = requests.post(url, data=json.dumps(datatest), headers={"Content-Type": "application/json"})

def move(*args):
    dor = directorauto()
    if dor == "auto":
        pyautogui.move(*args)
    if dor == "direct":
        pydirectinput.move(*args)
def press(key):
    pyautogui.press(key)

def senddata (url, context):
    data = {
    "embeds": [
        {
        "title": "Script Stats",
        "description": "User: " + context["user"] + "\nChannel: " + context["channel"],
        "fields": [
            {
            "name": "Current API Lists",
            "value": f"Mod List:\n```" + context["modlist"] + "```\n\nDev List:\n```" + context["devlist"]+ "```"
            },
            {
            "name": "Script Options",
            "value": context["options"]
            },
            {
            "name": "Machine Stats",
            "value": f"CPU Frequency: " + str(round(int(psutil.cpu_freq().current) / 1000, 2)) + " GHz\n\nTotal Usage: " + str(psutil.cpu_percent()) + "\n\nTotal Ram: " + str(get_size(psutil.virtual_memory().total)) + "\n\nTotal Ram Usage: " + str(get_size(psutil.virtual_memory().percent)) + "\n\nTotal Swap: " + str(get_size(psutil.swap_memory().total)) + "\n\nTotal Swap Usage: " + str(get_size(psutil.swap_memory().percent))
            }
        ]
        }
    ]
    }
    result = requests.post(url, data=json.dumps(data),
                           headers={"Content-Type": "application/json"})
