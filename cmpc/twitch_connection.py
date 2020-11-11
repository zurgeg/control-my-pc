from python_twitch_irc import TwitchIrc


class TwitchConnection(TwitchIrc):
    def on_connect(self):
        self.join(f'#{self._username}')
