# PSL Packages
import time
import logging as log

# PIP Packages;
import requests  # !modalert and chatrelay
import pyautogui
from pynput.mouse import Button

# Local Packages
from cmpc.utils import get_platform, move as move_mouse
import cmpc  # custom stuff we need
# from cmpc.keyboard_keycodes import KeyboardKeycodes


class CommandProcessor:
    """For processing Twitch Plays commands.

    Does not handle permissions, all commands are unrestricted.
    Public methods:
    process_commands
    Instance variables:
    config -- a dict of config values
    obs_file_handle -- object of the files containing the currently executing command
    mouse -- a pynput.mouse.Controller instance
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
        ('alt f4', 'quit',): ('altleft', 'f4',),
        ('alt tab', 'alt-tab',): ('altleft', 'tab',),
        ('screenshot', 'screen shot',): ('win', 'prtsc',),
    }

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
        ('light left', 'little left',): (-25, 0,),
        ('super light left', 'super little left',): (-10, 0,),
        ('right',): (100, 0,),
        ('light right', 'little right',): (25, 0,),
        ('super light right', 'super little right',): (10, 0,),
        ('up',): (0, -100,),
        ('light up', 'little up',): (0, -25,),
        ('super light up', 'super little up',): (0, -10,),
        ('down',): (0, 100,),
        ('light down', 'little down',): (0, 25,),
        ('super light down', 'super little down',): (0, 10,),
    }

    MOUSE_DRAG_COMMANDS = {
        ('drag up', 'drag mouse up',): (0, -50, 0.25,),
        ('drag down', 'drag mouse down',): (0, 50, 0.25,),
        ('drag right', 'drag mouse right',): (50, 0, 0.25,),
        ('drag left', 'drag mouse left',): (-50, 0, 0.25,),
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

    def __init__(self, config, obs_file_name, mouse):
        """"Initialise the class attributes"""
        self.config = config
        self.obs_file_name = obs_file_name
        self.mouse = mouse
        #self.twitch_username = TWITCH_USERNAME

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
            if comm(message):
                command_has_run = True
                break
        return command_has_run

    @staticmethod
    def remove_prefix(message, prefix) -> str:
        """Return the message with the prefix removed."""
        return message[len(prefix):]

    def error_handle(self, error, message):
        """Throw an error to here, and it will be dealt with"""
        # pass
        # log.error(f'ERROR CONTAINED: {error}')
        # cmpc.send_error(self.config['discord']['systemlog'], error,
        #                     message, 'UNKNOWN', self.twitch_username,
        #                     self.config['options']['DEPLOY'])
        # if self.config['options']['DEPLOY'] == "Debug":
        #     log.info('--ERROR IN CODE, SENDING TRACEBACK DUE TO DEBUG MODE--')
        #     raise error
        # else:
        #     pass

    def log_to_obs(self, message):
        """Log a message to the file shown on-screen for the stream."""
        if message is None:
            with open(self.obs_file_name, 'r') as obs_file_handle:
                current_obs_file_contents = obs_file_handle.read()
            if current_obs_file_contents == 'nothing':
                return
            else:
                with open(self.obs_file_name, 'w') as obs_file_handle:
                    obs_file_handle.write('nothing')
        else:
            with open(self.obs_file_name, 'w') as obs_file_handle:
                obs_file_handle.write(message.get_log_string())
            time.sleep(0.5)
            log.info(message.get_log_string())
            requests.post(self.config['discord']['chatrelay'],
                          json=message.get_log_webhook_payload(),
                          headers={'User-Agent': self.config['api']['useragent']})

    @staticmethod
    def _hold_key_pyautogui(key_to_press, time_value):
        """Hold the key for the duration specified."""
        log.debug('HONEY HE IS OFF THE DRUG!')
        pyautogui.keyDown(key_to_press)
        time.sleep(time_value)
        pyautogui.keyUp(key_to_press)

    def _process_key_press_commands(self, message) -> bool:
        """Check message for key press commands and run any applicable command.

        Presses the button and also calls log_to_obs.
        Takes a cmpc.TwitchMessage instance.
        Returns True if a command has been run and False otherwise.
        """
        for valid_inputs, output in self.KEY_PRESS_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
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
                self.mouse.press(Button.left)
                time.sleep(output)
                self.mouse.release(Button.left)
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
        """
        for valid_input in self.TYPE_COMMANDS:
            if message.content.startswith(valid_input):
                self.log_to_obs(message)
                try:
                    message_to_type = self.remove_prefix(message.original_content, valid_input)
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
                    time_value = float(self.remove_prefix(message.content, valid_input))
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
                        log.debug("WHAT HAPPENED TO MY SWEET BABY BOY!")
                        self._hold_key_pyautogui(output, time_value)
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
                'content': '<@&741308237135216650> https://twitch.tv/controlmypc',
            }
            log.info('[MODALERT] Sending request...')
            requests.post(self.config['discord']['chatalerts'],
                          json=data,
                          headers={'User-Agent': self.config['api']['useragent']})
            log.info('[MODALERT] Request sent')
            return True

        # 'go to' command
        if message.content.startswith('go to '):
            try:
                coord = self.remove_prefix(message.content, 'go to ')
                if coord == 'center':
                    xval, yval = tuple(res / 2 for res in pyautogui.size())
                else:
                    xval, yval = coord.split(' ', 1)
                xval = int(xval)
                yval = int(yval)
                pyautogui.moveTo(xval, yval)
                self.log_to_obs(message)
            except ValueError:
                log.error(f'Could not move mouse to location: {message.content}\nDue to non-numeric args')
            except pyautogui.PyAutoGUIException:
                log.error(f'Could not move mouse to location: {message.content}\nDue to pyautogui issue')
            except Exception as error:
                self.error_handle(error, message)
            return True

        # gtype command
        if message.content.startswith('gtype '):
            try:
                if get_platform() == 'darwin':
                    log.error(f'COULD NOT GTYPE: {message.content}\n'
                              'DUE TO PLATFORM: darwin')
                    return True
                try:
                    import pydirectinput
                    message_to_type = self.remove_prefix(message.content,
                                                         'gtype ')
                    pydirectinput.typewrite(message_to_type)
                except Exception:
                    log.error(f'COULD NOT GTYPE: {message.content}')
                return True
            except Exception as error:
                self.error_handle(error, message)

        # No commands run, sad cat hours
        return False
