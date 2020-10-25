import json
import toml
import sys

import requests
import pyautogui
import psutil


if sys.platform == "darwin":
    pass
else:
    import pydirectinput


__all__ = (
    'get_platform',
    'get_size',
    'send_webhook',
    'send_error',
    'move',
    'press',
    'send_data',
)


def get_platform():
    platform = sys.platform
    return platform


def get_size(value, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """

    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if value < factor:
            return f"{value:.2f}{unit}{suffix}"
        value /= factor


def direct_or_auto():
    platform = get_platform()
    if platform == "darwin":
        return 'auto'
    else:
        return 'direct'


def send_webhook(url, content):
    data = {"content": content}
    requests.post(url, data=data)


def send_error(url, error, msg, usr, channel):
    datatest = {"embeds": [{"title": "Script - Exception Occured","description": f"***Last Sent Message -*** {msg}\n\n***Exception Info -*** {error}\n\n[***Stream Link***](https://twitch.tv/{channel})","color": 1107600,"footer": {"text": 'User: ' + usr + ' - Channel: ' + channel,"icon_url": "https://blog.twitch.tv/assets/uploads/generic-email-header-1.jpg"}}]}
    requests.post(url, data=json.dumps(datatest), headers={"Content-Type": "application/json"})


def move(*args):
    dor = direct_or_auto()
    if dor == "auto":
        pyautogui.move(*args)
    if dor == "direct":
        pydirectinput.move(*args)


def press(key):
    pyautogui.press(key)


def send_data(url, context):
    machine_stats = "\n\n".join([
        f"CPU Frequency: {round(int(psutil.cpu_freq().current) / 1000, 2)} GHz",
        f"Total Usage: {psutil.cpu_percent()}%",
        f"Total Ram: {get_size(psutil.virtual_memory().total)}",
        f"Total Ram Usage: {get_size(psutil.virtual_memory().used)}",
        f"Total Swap: {get_size(psutil.swap_memory().total)}",
        f"Total Swap Usage: {get_size(psutil.swap_memory().used)}",
    ])
    options_str = '\n'.join([
        f"Log All: {context['options']['LOG_ALL']}",
        f"Start Message: {context['options']['START_MSG']}",
        f"EXC_MSG: {context['options']['EXC_MSG']}",
        f"Log PPR: {context['options']['LOG_PPR']}",
    ])
    data = {
        "embeds": [
            {
                "title": "Script Stats",
                "description": f"User: {context['user']}\nChannel: {context['channel']}",
                "fields": [
                    {
                        "name": "Current API Lists",
                        "value": f"Mod List:\n```\n{context['modlist']}```\n\nDev List:\n```\n{context['devlist']}```",
                    },
                    {
                        "name": "Script Options",
                        "value": options_str,
                    },
                    {
                        "name": "Machine Stats",
                        "value": machine_stats,
                    },
                ],
            },
        ],
    }
    requests.post(url, json=data)