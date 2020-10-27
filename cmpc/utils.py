import json
import toml
import sys

import requests
import pyautogui
import psutil

# Check if we are on a mac or not
if not sys.platform == "darwin":
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
    """Returns if we should use pydirectinput or pyautogui"""
    platform = get_platform()
    if platform == "darwin":
        return 'auto'
    else:
        return 'direct'


def send_webhook(url:str, content:str):
    """Sends a webhook to discord, takes (url, message)"""
    data = {"content": content}
    requests.post(url, data=data)


def send_error(url, error, msg, usr, channel):
    """Sends a error to discord"""
    datatest = {"embeds": [{"title": "Script - Exception Occured","description": f"***Last Sent Message -*** {msg}\n\n***Exception Info -*** {error}\n\n[***Stream Link***](https://twitch.tv/{channel})","color": 1107600,"footer": {"text": 'User: ' + usr + ' - Channel: ' + channel,"icon_url": "https://blog.twitch.tv/assets/uploads/generic-email-header-1.jpg"}}]}
    requests.post(url, data=json.dumps(datatest), headers={"Content-Type": "application/json"})


def move(*args):
    """Moves the mouse with cross-platform support"""
    dor = direct_or_auto()
    if dor == "auto":
        pyautogui.move(*args)
    if dor == "direct":
        pydirectinput.move(*args)


def press(key):
    """Presses a key (more functonality coming soon)"""
    pyautogui.press(key)


def send_data(url, context):
    """Dumps machine data, config, and api"""
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
        f"Environment: {context['options']['DEPLOY']}",
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