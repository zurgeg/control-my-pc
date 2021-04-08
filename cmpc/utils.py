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

# PIP Packages;
import requests
import pyautogui
import psutil

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


def mode_testing(environment, env_vars_used, branch):
    """Check if the script is in testing mode based on a number of factors.

    Args:
        environment -- DEPLOY constant from the CONFIG file, should be 'Production' or 'Debug'
        env_vars_used -- bool indicating if CONFIG has been pulled from environment variables
        branch -- the name of the git branch of the repo containing the script, if it exists
    Returns True if script should be in testing mode and False otherwise.
    """
    if environment == 'Debug' or env_vars_used or branch != 'master':
        return True
    else:
        return False


def running_as_admin():
    """Check if the program is running as admin.

    Returns True if the platform is not windows or if you're running as admin, False if not running as admin.
    """
    if sys.platform != 'win32':
        return True
    else:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()


def get_git_repo_info(default_branch_name='master'):
    """Try to get the name of the git branch containing the script.

    Args:
        default_branch_name -- this will be returned as branch_name if there is no git repo
    Returns:
        branch_name
        branch_name_assumed -- True if there was no git repo and branch name defaulted, False otherwise
    """
    try:
        # noinspection PyUnresolvedReferences
        import git
    except ImportError:
        branch_name = default_branch_name
        branch_name_assumed = True
    else:
        try:
            branch_name = git.Repo().active_branch.name
            branch_name_assumed = False
        except (ImportError, git.exc.GitError):
            branch_name = default_branch_name
            branch_name_assumed = True

    return branch_name, branch_name_assumed


def removeprefix(string: str, prefix: str, case_sensitive: bool = True):
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


def get_size(value, suffix='B'):
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


def direct_or_auto():
    """Return if we should use pydirectinput or pyautogui."""
    if sys.platform == 'win32':
        # Windows only, better compatibility with games
        return 'direct'
    else:
        # Default
        return 'auto'


def send_webhook(url: str, content: str):
    """Send a webhook to discord, takes (url, message)."""
    data = {'content': content}
    if url == "":
        return
    requests.post(url, data=data)


def send_error(url, error, t_msg, channel, environment, branch, branch_assumed):
    """Send info about an error to a discord webhook."""
    embed_description = f'***Last Sent Message -*** {t_msg.content}\n\n'\
                        f'***Exception Info -*** {error}\n\n'\
                        f'[***Stream Link***](https://twitch.tv/{channel})\n\n'\
                        f'**Environment -** {environment}'
    if branch != 'master':
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
    requests.post(url, data=json.dumps(data), headers={'Content-Type': 'application/json'})


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


def hold_mouse(time_value, *args, **kwargs):
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


def hold_key(time_value, *args, **kwargs):
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


def parse_goto_args(message, prefix):
    """Return the x and y coords. Used in go to and drag to commands."""
    coord = removeprefix(message.content, prefix)
    if coord in ['center', 'centre']:
        xval, yval = tuple(res / 2 for res in pyautogui.size())
    else:
        xval, yval = coord.split(' ', 1)
    xval = int(xval)
    yval = int(yval)

    return xval, yval


def send_data(url, context):
    """Dump machine data, CONFIG, and api info to a discord webhook."""
    machine_stats = '\n\n'.join([
        f'CPU Frequency: {round(int(psutil.cpu_freq().current) / 1000, 2)} GHz',
        f'Total Usage: {psutil.cpu_percent()}%',
        f'Total Ram: {get_size(psutil.virtual_memory().total)}',
        f'Total Ram Usage: {get_size(psutil.virtual_memory().used)}',
        f'Total Swap: {get_size(psutil.swap_memory().total)}',
        f'Total Swap Usage: {get_size(psutil.swap_memory().used)}',
    ])
    options_str = '\n'.join([
        f"Log All: {context['options']['LOG_ALL']}",
        f"Start Message: {context['options']['START_MSG']}",
        f"EXC_MSG: {context['options']['EXC_MSG']}",
        f"Log PPR: {context['options']['LOG_PPR']}",
        f"Environment: {context['options']['DEPLOY']}",
    ])
    data = {
        'embeds': [
            {
                'title': 'Script Stats',
                'description': f"User: {context['user']}\nChannel: {context['channel']}",
                'fields': [
                    {
                        'name': 'Current API Lists',
                        'value': f"Mod List:\n```\n{context['modlist']}```\n\nDev List:\n```\n{context['devlist']}```",
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
    requests.post(url, json=data)
