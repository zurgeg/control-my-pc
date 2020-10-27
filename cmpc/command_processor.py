import time
import logging as log

import requests
import pyautogui
from pynput.mouse import Button
from cmpc.utils import move as move_mouse
# from cmpc.keyboard_keycodes import KeyboardKeycodes

log.basicConfig(
    level=log.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        log.FileHandler("system.log"),
        log.StreamHandler()
    ]
)
class CommandProcessor(object):

    KEY_PRESS_COMMANDS = {
        ('enter',): 'enter',
        ('tab',): 'tab',
        ('esc', 'escape',): 'esc',
        ('windows key', 'win',): 'win',
        ('backspace', 'back space', 'delete',): 'backspace',
        ('space', 'spacebar',): 'space',
        # ('page up', 'pageup',): 'pageup',
        # ('page down', 'pagedown',): 'pagedown',
        # ('arrow down',): 'down',
        # ('arrow up',): 'up',
        # ('arrow left',): 'left',
        # ('arrow right',): 'right',
        ('refresh', 'F5'): 'f5',
        ('where', 'where?'): 'ctrl',
    }

    CLICK_COMMANDS = {
        ('click', 'left click',): 'left',
        ('doubleclick', 'double click',): 'doubleclick',
        ('rightclick', 'right click',): 'right',
        ('middleclick', 'middle click',): 'middle',
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
    }

    HOTKEY_COMMANDS = {
        ('control t', 'ctrl t', 'new tab',): ('ctrl', 'n',),
        ('control s', 'ctrl s', 'save',): ('ctrl', 's',),
        ('control z', 'undo',): ('ctrl', 'z',),
        ('control c', 'copy',): ('ctrl', 'c',),
        ('control v', 'paste',): ('ctrl', 'v',),
        ('control w', 'close tab', 'close the tab',): ('ctrl', 'w',),
        ('control a', 'select all', 'ctrl a',): ('ctrl', 'a',),
        ('control k', 'tayne', 'ctrl k',): ('ctrl', 'k',),
        ('quit', 'alt f4',): ('altleft', 'f4',),
        ('alt tab', 'alt-tab',): ('altleft', 'tab',),
        ('screenshot', 'screen shot',): ('win', 'prtsc',),
    }

    MOUSE_HOLD_COMMANDS = {
        ('hold mouse', 'hold the mouse',): 3,
        ('hold mouse long',): 9,
    }

    MOUSE_SCROLL_COMMANDS = {
        ('scroll down',): -60,
        ('scoll up',): 60,
    }

    MOUSE_DRAG_COMMANDS = {
        ('drag mouse up',): (0, -50, 0.25,),
        ('drag mouse down',): (0, 50, 0.25,),
        ('drag mouse right',): (50, 0, 0.25,),
        ('drag mouse left',): (-50, 0, 0.25,),
    }

    TYPE_COMMANDS = (
        'type ',
        'press ',
    )  # note trailing space - this is to process args better

    HOLD_KEY_COMMANDS = (
        'd for ',
        'a for ',
        's for ',
        'w for ',
        'arrow up for ',
        'arrow left for ',
        'arrow right for ',
        'arrow down for ',
    )  # note trailing space - this is to process args better

    def __init__(self, config, obs_file_handle, mouse):
        self.config = config
        self.obs_file_handle = obs_file_handle
        self.mouse = mouse

    def process_commands(self, message) -> bool:
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
            # self._process_hold_key_commands,
        ]

        command_has_run = False
        for comm in commands:
            if comm(message):
                command_has_run = True
                break
        return command_has_run

    @staticmethod
    def remove_prefix(message, prefix) -> str:
        return message[len(prefix):]

    def log_to_obs(self, message):
        """
        Log a message to the file shown on-screen for the stream
        """

        self.obs_file_handle.truncate()
        if message is None:
            self.obs_file_handle.seek(0, 0)
            self.obs_file_handle.write("nothing")
            return

        self.obs_file_handle.seek(0, 0)
        self.obs_file_handle.write(message.get_log_string())
        time.sleep(0.5)
        log.info(message.get_log_string())
        requests.post(self.config['discord']['chatrelay'], json=message.get_log_webhook_payload(), headers={'User-Agent': self.config['api']['useragent']})

    def _process_key_press_commands(self, message) -> bool:
        for valid_inputs, output in self.KEY_PRESS_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                pyautogui.press(output)
                return True
        return False

    def _process_click_commands(self, message) -> bool:
        for valid_inputs, output in self.CLICK_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                click_count = 1
                if output == 'doubleclick':
                    click_count = 2
                pyautogui.click(button=output, clicks=click_count)
                return True
        return False

    def _process_mouse_move_commands(self, message) -> bool:
        for valid_inputs, output in self.MOUSE_MOVE_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                move_mouse(*output)
                return True
        return False

    def _process_hotkey_commands(self, message) -> bool:
        for valid_inputs, output in self.KEY_PRESS_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                pyautogui.hotkey(*output)
                return True
        return False

    def _process_mouse_hold_commands(self, message) -> bool:
        for valid_inputs, output in self.KEY_PRESS_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                self.mouse.press(Button.left)
                time.sleep(output)
                self.mouse.release(Button.left)
                return True
        return False

    def _process_mouse_scroll_commands(self, message) -> bool:
        for valid_inputs, output in self.MOUSE_SCROLL_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                for _ in range(5):
                    pyautogui.scroll(output)
                return True
        return False

    def _process_mouse_drag_commands(self, message) -> bool:
        for valid_inputs, output in self.MOUSE_SCROLL_COMMANDS.items():
            if message.content in valid_inputs:
                self.log_to_obs(message)
                pyautogui.drag(*output, button='left')
                return True
        return False

    def _process_misc_commands(self, message) -> bool:
        """
        Here's where we put the stuff that's either too complicated to dict, or just a one-off irregular
        """

        # !modalert command
        if message.content in ['!modalert']:
            log.info('[MODALERT] called.')
            data = {
                'embeds': [
                    {'title': ':rotating_light: **The user above needs a moderator on the stream.** :rotating_light:'}
                ],
                'username': message.username,
                'content': '<@&741308237135216650> https://twitch.tv/controlmypc',
            }
            log.info('[MODALERT] Sending request...')
            requests.post(self.config['discord']['chatalerts'], json=data, headers={'User-Agent': self.config['api']['useragent']})
            log.info('[MODALERT] Request sent')
            return True

        # "go to" command
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
            except Exception:
                log.error(f'Could not move mouse to location: {message.content}')
            return True

        # No comamnds run, sad cat hours
        return False

    def _process_type_commands(self, message) -> bool:
        for valid_input in self.TYPE_COMMANDS:
            if message.content.startswith(valid_input):
                self.log_to_obs(message)
                try:
                    message_to_type = self.remove_prefix(message.original_content, valid_input)
                    pyautogui.typewrite(message_to_type)
                except Exception:
                    log.error(f'COULD NOT TYPE: {message.content}')
                return True
        return False

    # def _process_hold_key_commands(self, message) -> bool:
    #     for valid_input in self.HOLD_KEY_COMMANDS:
    #         if message.content.startswith(valid_input):
    #             try:
    #                 time_value = float(self.remove_prefix(message.content, valid_input))

    #                 # This command is a lil more complex bc we need to work out what key they actually want to press,
    #                 # but still nothing impossible
    #                 key_to_press = {
    #                     'd': KeyboardKeycodes.D,
    #                     'a': KeyboardKeycodes.A,
    #                     's': KeyboardKeycodes.S,
    #                     'w': KeyboardKeycodes.W,
    #                     'arrow up': KeyboardKeycodes.UP_ARROW,
    #                     'arrow left': KeyboardKeycodes.LEFT_ARROW,
    #                     'arrow right': KeyboardKeycodes.RIGHT_ARROW,
    #                     'arrow down': KeyboardKeycodes.DOWN_ARROW,
    #                 }.get(valid_input[:-4])
    #                 assert key_to_press is not None

    #                 if 0 >= time_value <= 10:
    #                     self.log_to_obs(message)
    #                     PressAndHoldKey(key_to_press, time_value)
    #             except Exception:
    #                 print(f'Error holding key: {message.content}')
    #             return True
    #     return False
