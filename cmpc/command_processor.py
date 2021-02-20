"""Processes and executes commands.

Classes:
    CommandProcessor -- processes commands, includes helper methods like log_to_obs
"""

# PSL Packages
import time
import sys
import json
import logging as log
from pathlib import Path

# PIP Packages;
import requests  # !modalert and chatrelay
import pyautogui
import pyperclip  # for ptype command

# Local Packages
from cmpc.utils import removeprefix, twitch_api_get_user, move_mouse, hold_mouse, press_key, hold_key, parse_goto_args, send_webhook


CONFIG_FOLDER = Path('config/')


class CommandProcessor:
    """For processing Twitch Plays commands.

    Does not handle permissions, all commands are unrestricted.
    Public methods:
        process_commands
    Instance variables:
        config -- a dict of config values
        obs_file_name -- path to the file containing the currently executing command
        obs_log_sleep_duration -- how long to leave executing.txt to make it readable on obs on stream
    """

    KEY_PRESS_COMMANDS = {
        ('enter',): 'enter',
        ('tab',): 'tab',
        ('esc', 'escape',): 'esc',
        ('windows key', 'win',): 'win',
        ('backspace', 'back space', 'delete',): 'backspace',
        ('space', 'spacebar', 'space bar'): 'space',
        ('page up', 'pageup',): 'pageup',
        ('page down', 'pagedown',): 'pagedown',
        ('arrow down',): 'down',
        ('arrow up',): 'up',
        ('arrow left',): 'left',
        ('arrow right',): 'right',
        ('refresh', 'F5'): 'f5',
        ('where', 'where?'): 'ctrl',
    }

    HOTKEY_COMMANDS = {
        ('control t', 'ctrl t', 'new tab',): ('ctrl', 't',),
        ('control s', 'ctrl s', 'save',): ('ctrl', 's',),
        ('control z', 'ctrl z', 'undo',): ('ctrl', 'z',),
        ('control c', 'ctrl s', 'copy',): ('ctrl', 'c',),
        ('control v', 'ctrl v', 'paste',): ('ctrl', 'v',),
        ('control w', 'ctrl w', 'close tab', 'close the tab',): ('ctrl', 'w',),
        ('control a', 'ctrl a', 'select all',): ('ctrl', 'a',),
        ('control k', 'ctrl k', 'tayne',): ('ctrl', 'k',),
        ('control /', 'ctrl /',): ('ctrl', '/'),
        ('quit',): ('altleft', 'f4',),
        ('alt tab', 'alt-tab',): ('altleft', 'tab',),
        ('screenshot', 'screen shot',): ('win', 'prtsc',),
    }

    # note that here doubleclick is not actually a valid pyautogui input, but it gets fixed in the actual def later on
    CLICK_COMMANDS = {
        ('click', 'leftclick', 'left click',): 'left',
        ('doubleclick', 'double click',): 'doubleclick',
        ('rightclick', 'right click',): 'right',
        ('middleclick', 'middle click',): 'middle',
    }

    MOUSE_HOLD_COMMANDS = {
        ('hold mouse', 'hold the mouse',): 3,
        ('hold mouse long', 'hold the mouse long',): 9,
    }

    MOUSE_SCROLL_COMMANDS = {
        ('scroll down',): -60,
        ('scroll up',): 60,
    }

    MOUSE_MOVE_COMMANDS = {
        ('left',): (-100, 0,),
        ('light left', 'little left', 'slight left',): (-25, 0,),
        ('super light left', 'super little left', 'super slight left',): (-10, 0,),
        ('right',): (100, 0,),
        ('light right', 'little right', 'slight right',): (25, 0,),
        ('super light right', 'super little right', 'super slight right',): (10, 0,),
        ('up',): (0, -100,),
        ('light up', 'little up', 'slight up',): (0, -25,),
        ('super light up', 'super little up', 'super slight up',): (0, -10,),
        ('down',): (0, 100,),
        ('light down', 'little down', 'slight down',): (0, 25,),
        ('super light down', 'super little down', 'super slight down',): (0, 10,),
    }

    MOUSE_DRAG_COMMANDS = {
        ('drag up', 'drag mouse up',): (0, -50, 0.75,),
        ('drag down', 'drag mouse down',): (0, 50, 0.75,),
        ('drag right', 'drag mouse right',): (50, 0, 0.75,),
        ('drag left', 'drag mouse left',): (-50, 0, 0.75,),
    }

    TYPE_COMMANDS = (
        'type ',
        'press ',
    )  # note trailing space - this is to process args better

    HOLD_KEY_COMMANDS = {
        'd for ': 'd',
        'a for ': 'a',
        's for ': 's',
        'w for ': 'w',
        'arrow up for ': 'up',
        'arrow left for ': 'left',
        'arrow right for ': 'right',
        'arrow down for ': 'down',
    }  # note trailing space - this is to process args better

    def __init__(self, config, obs_file_name, req_account_age_days=None, obs_log_sleep_duration=None):
        """Initialise the class attributes."""
        self.config = config
        self.obs_file_name = obs_file_name
        if req_account_age_days is None:
            self.req_account_age_days = 7
        else:
            self.req_account_age_days = req_account_age_days
        if obs_log_sleep_duration is None:
            self.obs_log_sleep_duration = 0.5
        else:
            self.obs_log_sleep_duration = obs_log_sleep_duration

        self.cooldowns = {
            '!modalert': {'required': 30.0, 'last_called': 0.0},
        }

    def process_commands(self, message) -> bool:
        """Check a Twitch message for command invocations and run any applicable command.

        Will run the first applicable command before returning.
        Args:
            message -- a cmpc.TwitchMessage object
        Returns:
            command_has_run
        """
        commands = [
            self._process_key_press_commands,
            self._process_click_commands,
            self._process_mouse_move_commands,
            self._process_hotkey_commands,
            self._process_mouse_hold_commands,
            self._process_mouse_scroll_commands,
            self._process_mouse_drag_commands,
            self._process_misc_commands,
            self._process_type_commands,
            self._process_hold_key_commands,
        ]

        command_has_run = False
        for comm in commands:
            # noinspection PyArgumentList
            if comm(message):
                command_has_run = True
                break
        return command_has_run

    def error_handle(self, error, message):
        """Throw an error to here, and it will be dealt with."""
        # pass
        # log.error(f'ERROR CONTAINED: {error}')
        # cmpc.send_error(self.CONFIG['discord']['systemlog'], error,
        #                     message, 'UNKNOWN', self.twitch_username,
        #                     self.CONFIG['options']['DEPLOY'])
        # if self.CONFIG['options']['DEPLOY'] == "Debug":
        #     log.info('--ERROR IN CODE, SENDING TRACEBACK DUE TO DEBUG MODE--')
        #     raise error
        # else:
        #     pass

    # TODO: separate log_to_obs and logging commands to the systemlog somewhat
    def log_to_obs(self, message, none_log_msg='nothing', sleep_duration=None, none_sleep=False):
        """Log a message to the file shown on-screen for the stream."""
        # Default log duration
        if sleep_duration is None:
            sleep_duration = self.obs_log_sleep_duration

        if message is None:
            with open(self.obs_file_name, 'w', encoding='utf-8') as obs_file_handle:
                obs_file_handle.write(none_log_msg)
            if none_sleep:
                time.sleep(sleep_duration)
        else:
            with open(self.obs_file_name, 'w', encoding='utf-8') as obs_file_handle:
                obs_file_handle.write(message.get_log_string())

            time.sleep(sleep_duration)
            log.info(message.get_log_string())
            requests.post(self.config['discord']['chatrelay'],
                          json=message.get_log_webhook_payload(),
                          headers={'User-Agent': self.config['api']['useragent']})

    def check_user_allowed(self, user_id, user_info_cache, cache_file_path=CONFIG_FOLDER / 'user_info_cache.json'):
        """Check whether a Twitch user account is old enough to run commands.

        Args:
            user_id -- Twitch account ID to get info on from their API
            cache_file_path -- JSON file to store info about users in. May be modified by this function.
        Returns a boolean which will be True if the user's account age was verified.

        Account age is checked against self.req_account_age_days.
        Also checks if the user has been manually banned or allowed.
        """
        # TODO: split into smaller functions e.g. check_user_cache and check_user_twitch_api?
        # TODO: for performance, backup the cache occasionally, instead of every write?
        user_id = str(user_id)

        # If the user is in the cache get their info from the cache
        if user_id in user_info_cache:
            cached_user_info = user_info_cache[user_id]

            force_wait = cached_user_info.get('force_wait')
            # If they're marked as allow or block, return that
            if 'allow' in cached_user_info and not force_wait:
                return cached_user_info['allow']
            # If they're not marked, check the cached allow time
            elif time.time() > cached_user_info['allow_after']:
                user_info_cache[user_id]['allow'] = True
                if cached_user_info.get('force_wait'):
                    cached_user_info['force_wait'] = False
                with open(cache_file_path, 'w') as user_info_cache_file:
                    json.dump(user_info_cache, user_info_cache_file)

                return True
            else:
                return False
        # Else, try to get it from the Twitch API
        else:
            try:
                api_user_info, response = twitch_api_get_user(self.config['twitch']['api_client_id'],
                                                    removeprefix(self.config['twitch']['oauth_token'], 'oauth:'),
                                                    user_id=user_id)
            except requests.RequestException:
                # No luck, no allow
                send_webhook(self.config['discord']['systemlog'], f"Failed to get info on user from twitch api.\nStatus Code - {response.status_code}")
                return False
            else:
                # Check the status from the response info, and save it to the cache
                account_created_string = api_user_info['created_at']
                account_created_seconds = time.mktime(time.strptime(account_created_string, '%Y-%m-%dT%H:%M:%S.%fZ'))
                # allow_after should be the time in seconds since the epoch after which the user is allowed
                allow_after_time = account_created_seconds + (self.req_account_age_days * 24 * 60**2)

                user_info_cache[user_id] = {}
                if allow_after_time < time.time():
                    user_info_cache[user_id]['allow'] = True
                    return_value = True
                else:
                    user_info_cache[user_id]['allow_after'] = allow_after_time
                    return_value = False

                # Update the cache file
                with open(cache_file_path, 'w') as user_info_cache_file:
                    json.dump(user_info_cache, user_info_cache_file)

                return return_value

    def _process_key_press_commands(self, message) -> bool:
        """Check message for key press commands and run any applicable command.

        Presses the button and also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.KEY_PRESS_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                if 'enter' in valid_inputs:
                    press_key(output)
                else:
                    pyautogui.press(output)

                return True
        return False

    def _process_hotkey_commands(self, message) -> bool:
        """Check message for hotkey commands and run any applicable command.

        Presses the two keys together and also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.HOTKEY_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                pyautogui.hotkey(*output)
                return True
        return False

    def _process_click_commands(self, message) -> bool:
        """Check message for mouse click press commands and run any applicable command.

        Clicks the mouse button once, or twice if the command is named doubleclick.
        Also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.CLICK_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                click_count = 1
                if output == 'doubleclick':
                    click_count = 2
                    output = 'left'
                pyautogui.click(button=output, clicks=click_count)
                return True
        return False

    def _process_mouse_hold_commands(self, message) -> bool:
        """Check message for mouse hold commands and run any applicable command.

        Presses the left mouse button for the duration of time associated with the command.
        Also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.MOUSE_HOLD_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                hold_mouse(time_value=output, button='left')
                return True
        return False

    def _process_mouse_scroll_commands(self, message) -> bool:
        """Check message for mouse scroll commands and run any applicable command.

        Scrolls the mouse wheel five times by the amount associated with the command.
        Also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.MOUSE_SCROLL_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                for i in range(5):
                    pyautogui.scroll(output)
                return True
        return False

    def _process_mouse_move_commands(self, message) -> bool:
        """Check message for mouse move commands and run any applicable command.

        Moves the mouse by the command's co-ords and also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.MOUSE_MOVE_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                move_mouse(*output)
                return True
        return False

    def _process_mouse_drag_commands(self, message) -> bool:
        """Check message for mouse drag commands and run any applicable command.

        Moves the mouse by the commands co-ords while holding the left mouse button.
        Also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.MOUSE_DRAG_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                pyautogui.drag(*output, button='left')
                return True
        return False

    def _process_type_commands(self, message) -> bool:
        """Check message for typing commands and run any applicable command.

        Types the message and also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        This only handles regular typing, not ptype or gtype.
        """
        for valid_input in self.TYPE_COMMANDS:
            if message.content.startswith(valid_input):
                self.log_to_obs(message)
                try:
                    message_to_type = removeprefix(message.original_content, valid_input)
                    pyautogui.typewrite(message_to_type)
                except Exception as error:
                    self.error_handle(error, message)
                return True
        return False

    def _process_hold_key_commands(self, message) -> bool:
        """Check message for key press commands and run any applicable command.

        Holds the key for the duration specified in the message.
        Duration must be between 0 and 10 seconds or the keypress will not execute.
        Also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_input, output in self.HOLD_KEY_COMMANDS.items():
            if message.content.startswith(valid_input):
                try:
                    time_value = float(removeprefix(message.content, valid_input))
                    log.debug(f"time_value: {time_value}")
                    log.debug(f"key_to_press: {output}")

                    # This command is a lil more complex bc we need to work out what key they actually want to press,
                    # but still nothing impossible
                    log.debug('i am the boss, and i give all the orders')
                    if output is None:
                        log.debug('no key to press, im having sad cat hours ngl...')
                        return False

                    log.debug('And when we split, we split my way.')
                    if 0.0 < time_value <= 10.0:
                        log.debug('time was a success')
                        self.log_to_obs(message)
                        hold_key(key=output, time_value=time_value)
                except Exception as error:
                    self.error_handle(error, message)
                return True
        return False

    def _process_misc_commands(self, message) -> bool:
        """Process commands that are either too complicated to dict, or just one-off irregulars.

        Runs the first applicable command and returns.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        # !modalert command
        if message.content.startswith('!modalert'):
            log.info('[MODALERT] called.')
            # Check cooldown
            time_since_last_called = time.time() - self.cooldowns['!modalert']['last_called']
            cooldown_ok = (time_since_last_called > self.cooldowns['!modalert']['required'])

            if cooldown_ok:
                self.cooldowns['!modalert']['last_called'] = time.time()

                data = {
                    'embeds': [
                        {
                            'title': ':rotating_light: '
                                     '**The user above needs a moderator on the stream.** '
                                     ':rotating_light:',
                            'description': f'Extra info: *{message.content[10:] or "none given"}*'
                        }
                    ],
                    'username': message.username,
                    'content': f"{self.config['discord']['modalertping']} "
                               f"https://twitch.tv/{self.config['twitch']['channel_to_join']}",
                }
                log.info('[MODALERT] Sending request...')
                # TODO: Move this requests over to cmpc package, so that way we can check if there is even a webhook
                #  set if not, then log what should have been sent to console.
                requests.post(self.config['discord']['chatalerts'],
                              json=data,
                              headers={'User-Agent': self.config['api']['useragent']})
                log.info('[MODALERT] Request sent')
                return True
            else:
                log.info('[MODALERT] still on cooldown.')

        # 'go to' command
        if message.content.startswith('go to '):
            try:
                xval, yval = parse_goto_args(message, 'go to ')
            except ValueError:
                log.error(f'Could not move mouse to location: {message.content} due to non-numeric or not enough args')
            except pyautogui.PyAutoGUIException:
                log.error(f'Could not move mouse to location: {message.content} due to pyautogui issue')
            except Exception as error:
                self.error_handle(error, message)
            else:
                self.log_to_obs(message)
                pyautogui.moveTo(xval, yval, duration=0.11)

                return True

        # 'drag to' command
        if message.content.startswith('drag to '):
            try:
                xval, yval = parse_goto_args(message, 'drag to ')
            except ValueError:
                log.error(f'Could not drag mouse to location: {message.content} due to non-numeric or not enough args')
            except pyautogui.PyAutoGUIException:
                log.error(f'Could not drag mouse to location: {message.content} due to pyautogui issue')
            except Exception as error:
                self.error_handle(error, message)
            else:
                self.log_to_obs(message)
                pyautogui.dragTo(xval, yval, duration=0.11)

                return True

        # gtype command
        # you don't say?
        if message.content.startswith('gtype '):
            try:
                if sys.platform == 'darwin':
                    log.error(f'COULD NOT GTYPE: {message.content}\n'
                              'DUE TO PLATFORM: darwin')
                    return True

                self.log_to_obs(message)
                import pydirectinput
                message_to_type = removeprefix(message.content, 'gtype ')
                pydirectinput.typewrite(message_to_type)
                return True
            except Exception as error:
                self.error_handle(error, message)

        # uses copy-paste instead of typing emulation
        if message.content.startswith('ptype '):
            self.log_to_obs(message)
            message_to_type = removeprefix(message.content, 'ptype ')

            try:
                pyperclip.copy(message_to_type)
            except pyperclip.PyperclipException:
                log.error(f'Could not ptype: {message.content}', sys.exc_info())
            else:
                pyautogui.hotkey('ctrl', 'v')

            return True

        # No commands run, sad cat hours
        return False
