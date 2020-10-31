# All packages are part of the PSL
import socket
import sys
import re
import typing
import time
import logging as log

log.basicConfig(
    level=log.INFO,
    format="[%(levelname)s] %(message)s",
    handlers=[
        log.FileHandler("system.log"),
        log.StreamHandler()
    ]
)


class Twitch(object):

    def __init__(self):
        self.user = None
        self.oauth = None
        self.socket = None

    def _twitch_login_status(self, data:bytes) -> bool:
        """Check the login data to see if login was successful

        Args:
            data (bytes): RThe IRC data from Twitch

        Returns:
            bool: Whether or not the login was successful
        """

        if not re.match(rb'^:(testserver\.local|tmi\.twitch\.tv) NOTICE \* :Login unsuccessful\r\n$', data):
            return True
        return False

    def twitch_connect(self, user: str, key: str) -> None:
        """Makes a socket connection to Twitch.tv

        Args:
            user (str): The username for the account
            key (str): The twitch oauth token for the account
        """

        self.user = user
        self.oauth = key
        log.info("[TWITCH] Trying to connect")

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(0.6)
        connect_host = "irc.twitch.tv"
        connect_port = 6667

        try:
            self.socket.connect((connect_host, connect_port))
        except Exception as e:
            log.warning(f"[TWITCH] Failed to connect, Sleeping for 5 seconds for reason: {e}")
            time.sleep(5)
            log.info("[TWITCH] Reconnecting after 5 seconds")
            return self.twitch_connect(self.user, self.oauth)

        log.info("[TWITCH] Connected, sending auth")
        self.socket.send(b'USER %s\r\n' % user.encode())
        self.socket.send(b'PASS %s\r\n' % key.encode())
        self.socket.send(b'NICK %s\r\n' % user.encode())

        if not self._twitch_login_status(self.socket.recv(1024)):
            log.error("[TWITCH] Auth denied!")
            exit(3)
        else:
            log.info("[TWITCH] Auth accepted and we are connected to twitch")
            self.socket.send(b'JOIN #%s\r\n' % user.encode())
            self.socket.recv(1024)

    def _check_has_message(self, data: bytes):
        return re.match(rb'^:[a-zA-Z0-9_]+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+(\.tmi\.twitch\.tv|\.testserver\.local)'
                        rb' PRIVMSG #[a-zA-Z0-9_]+ :.+$', data)

    def _parse_message(self, data: bytes):
        return {
            'channel': re.findall(rb'^:.+\![a-zA-Z0-9_]+@[a-zA-Z0-9_]+.+ PRIVMSG (.*?) :', data)[0],
            'username': re.findall(rb'^:([a-zA-Z0-9_]+)\!', data)[0],
            'message': re.findall(rb'PRIVMSG #[a-zA-Z0-9_]+ :(.+)', data)[0].decode('utf_8')
        }

    def twitch_receive_messages(self, amount: int=1024) -> typing.List[bytes]:
        """Receives data from the websocket and returns the lines

        Args:
            amount (int, optional): The number of bytes to receive

        Returns:
            typing.List[bytes]: A list of received messages
        """

        try:
            data = self.socket.recv(amount)
        except Exception:
            return list()

        if not data:
            log.warning("[TWITCH] Connection lost, trying to reconnect")
            self.twitch_connect(self.user, self.oauth)
            return list()

        if self._check_has_message(data):
            return [self._parse_message(line) for line in [_f for _f in data.split(b'\r\n') if _f]]
