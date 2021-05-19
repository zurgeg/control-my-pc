"""Helper functions for cmpc.

Functions:
    mode_testing -- take a number of things into account to see if script is in testing mode
    get_get_repo_info -- self explanatory
    removeprefix -- self explanatory, builtin as of 3.9 but here for compatibility with prior versions
    get_size -- for encoding large numbers into SI prefixes
    direct_or_auto -- returns 'auto' or 'direct' based on platform
    send_webhook -- simplifies sending of basic messages to discord webhooks
    send_error -- sends info on an unexpected exception to a discord webhook in embed form
    input_handler -- returns pyautogui or pydirectinput based on platform
    move_mouse -- moves the mouse with either pyautogui or pydirectinput situtationally
    hold_mouse -- holds the mouse with either pyautogui or pydirectinput situtationally
    press_key -- presses a key with either pyautogui or pydirectinput situtationally
    hold_mouse -- holds a key with either pyautogui or pydirectinput situtationally
    send_data -- gets info about the environment of the script and sends it to a discord webhook
    running_as_admin -- checks whether running as admin
"""

# PSL Packages;
import time
import json
import sys
import typing
import re
from pathlib import Path

# PIP Packages;
import aiohttp
import requests
import pyautogui
import psutil

from cmpc.twitch_message import TwitchMessage
import cmpc.permission_handler

# Check if we are on windows
if sys.platform == 'win32':
    import pydirectinput
    pydirectinput.FAILSAFE = False


__all__ = (
    'mode_testing',
    'get_git_repo_info',
    'removeprefix',
    'get_size',
    'direct_or_auto',
    'send_webhook',
    'send_error',
    'input_handler',
    'move_mouse',
    'hold_mouse',
    'press_key',
    'hold_key',
    'parse_goto_args',
    'send_data',
    'running_as_admin',
)


def mode_testing(environment: str, env_vars_used: bool, branch: str) -> bool:
    """Check if the script is in testing mode based on a number of factors.

    Args:
        environment -- DEPLOY constant from the CONFIG file, should be 'Production' or 'Debug'
        env_vars_used -- bool indicating if CONFIG has been pulled from environment variables
        branch -- the name of the git branch of the repo containing the script, if it exists
    Returns True if script should be in testing mode and False otherwise.
    """
    if environment == 'Debug' or env_vars_used or branch != 'main':
        return True
    else:
        return False


def running_as_admin() -> bool:
    """Check if the program is running as admin.

    Returns True if the platform is not windows or if you're running as admin, False if not running as admin.
    """
    if sys.platform != 'win32':
        return True
    else:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()


def get_git_repo_info(default_branch_name='main') -> typing.Tuple[str, bool]:
    """Try to get the name of the git branch containing the script.

    Args:
        default_branch_name -- this will be returned as branch_name if there is no git repo
    Returns:
        branch_name
        branch_name_assumed -- True if there was no git repo and branch name defaulted, False otherwise
    """
    head_file_path = Path('.git') / 'HEAD'

    try:
        head_file_contents = head_file_path.read_text()
        re_match = re.search('ref: refs/heads/(.*)\n', head_file_contents)
        if re_match is None:
            branch_name = f'(detached HEAD {head_file_contents})'
        else:
            branch_name = re_match[1]
    except FileNotFoundError:
        branch_name = default_branch_name
        branch_name_assumed = True
    else:
        branch_name_assumed = False

    return branch_name, branch_name_assumed


def removeprefix(string: str, prefix: str, case_sensitive: bool = True) -> str:
    """Remove a prefix from a string.

    For compatibility with pre-3.9.
    See here: https://docs.python.org/3/library/stdtypes.html#str.removeprefix
    From that link:
    If the string starts with the prefix string, return string[len(prefix):]. Otherwise, return a copy of the original
    string.
    Adds the custom argument case_sensitive. If this argument is False, the prefix will be removed regardless of case,
    but the returned string will be in the original case
    """
    if (not case_sensitive and string.lower().startswith(prefix.lower())) or string.startswith(prefix):
        return string[len(prefix):]
    else:
        return string


def get_size(value: float, suffix: str = 'B') -> str:
    """Scale bytes to its proper format.

    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if value < factor:
            return f'{value:.2f}{unit}{suffix}'
        value /= factor


def direct_or_auto() -> str:
    """Return if we should use pydirectinput or pyautogui."""
    if sys.platform == 'win32':
        # Windows only, better compatibility with games
        return 'direct'
    else:
        # Default
        return 'auto'


def send_webhook(url: str, content: str):
    """Send a webhook to discord."""
    data = {'content': content}
    if url == "":
        return
    requests.post(url, data=data)


async def send_error(
        url: str, error: Exception, t_msg: TwitchMessage, channel: str, environment: str, branch: str,
        branch_assumed: bool
):
    """Send info about an error to a discord webhook."""
    embed_description = f'***Last Sent Message -*** {t_msg.content}\n\n'\
                        f'***Exception Info -*** {error}\n\n'\
                        f'[***Stream Link***](https://twitch.tv/{channel})\n\n'\
                        f'**Environment -** {environment}'
    if branch != 'main':
        if branch_assumed:
            branch = branch + ' (unknown)'
        embed_description = embed_description + f'\n\n**Branch -** {branch}'

    data = {
        'content': '' if environment == 'Debug' else '<@&779783726196064323>',
        'embeds': [
            {
                'title': 'Script - Exception Occurred',
                'description': embed_description,
                'color': 1107600,
                'footer': {
                    'text': f'User: {t_msg.username} - Channel: {channel}',
                    'icon_url': 'https://blog.twitch.tv/assets/uploads/generic-email-header-1.jpg'
                }
            }
        ]
    }
    async with aiohttp.ClientSession() as session:
        session.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})


def input_handler():
    """Return pyautogui or pydirectinput based on platform."""
    dor = direct_or_auto()

    handler = pyautogui
    if dor == 'auto':
        handler = pyautogui
    elif dor == 'direct':
        handler = pydirectinput

    return handler


def move_mouse(*args, **kwargs):
    """Move the mouse, with cross-platform support."""
    dor = direct_or_auto()
    if dor == 'auto':
        pyautogui.move(*args, **kwargs)
    if dor == 'direct':
        pydirectinput.move(*args, **kwargs)


def hold_mouse(time_value: float, *args, **kwargs):
    """Hold a mouse button, with cross-platform support."""
    dor = direct_or_auto()
    handler = pyautogui
    if dor == 'auto':
        handler = pyautogui
    elif dor == 'direct':
        handler = pydirectinput
    handler.mouseDown(*args, **kwargs)
    time.sleep(time_value)
    handler.mouseUp(*args, **kwargs)


def press_key(*args, **kwargs):
    """Press a key , with cross-platform support."""
    dor = direct_or_auto()
    if dor == 'auto':
        pyautogui.press(*args, **kwargs)
    if dor == 'direct':
        pydirectinput.press(*args, **kwargs)


def hold_key(time_value: float, *args, **kwargs):
    """Hold a key, with cross-platform support."""
    dor = direct_or_auto()
    handler = pyautogui
    if dor == 'auto':
        handler = pyautogui
    elif dor == 'direct':
        handler = pydirectinput
    handler.keyDown(*args, **kwargs)
    time.sleep(time_value)
    handler.keyUp(*args, **kwargs)


def parse_goto_args(message: TwitchMessage, prefix: str):
    """Return the x and y coords. Used in go to and drag to commands."""
    coord = removeprefix(message.content, prefix)
    if coord in ['center', 'centre']:
        xval, yval = tuple(res / 2 for res in pyautogui.size())
    else:
        xval, yval = coord.split(' ', 1)
    xval = int(xval)
    yval = int(yval)

    return xval, yval


async def send_data(url: str, config: dict, user_permissions: typing.Dict[str, cmpc.permission_handler.Permissions]):
    """Dump machine data, config, and api info to a discord webhook."""
    machine_stats = '\n\n'.join([
        f'CPU Frequency: {round(int(psutil.cpu_freq().current) / 1000, 2)} GHz',
        f'Total Usage: {psutil.cpu_percent()}%',
        f'Total Ram: {get_size(psutil.virtual_memory().total)}',
        f'Total Ram Usage: {get_size(psutil.virtual_memory().used)}',
        f'Total Swap: {get_size(psutil.swap_memory().total)}',
        f'Total Swap Usage: {get_size(psutil.swap_memory().used)}',
    ])
    options_str = '\n'.join([
        f"Log All: {config['options']['LOG_ALL']}",
        f"Start Message: {config['options']['START_MSG']}",
        f"EXC_MSG: {config['options']['EXC_MSG']}",
        f"Log PPR: {config['options']['LOG_PPR']}",
        f"Environment: {config['options']['DEPLOY']}",
    ])
    modlist = [u for u in user_permissions if user_permissions[u].moderator]
    devlist = [u for u in user_permissions if user_permissions[u].developer]

    data = {
        'embeds': [
            {
                'title': 'Script Stats',
                'description': f"User: {config['twitch']['username']}\nChannel: {config['twitch']['channel_to_join']}",
                'fields': [
                    {
                        'name': 'Current API Lists',
                        'value': f'Mod List:\n```\n{modlist}```\n\nDev List:\n```\n{devlist}```\n'
                                 'https://api.cmpc.live/',
                    },
                    {
                        'name': 'Script Options',
                        'value': options_str,
                    },
                    {
                        'name': 'Machine Stats',
                        'value': machine_stats,
                    },
                ],
            },
        ],
    }
    async with aiohttp.ClientSession() as session:
        await session.post(url, json=data)
