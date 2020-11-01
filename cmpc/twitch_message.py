import time


class TwitchMessage:
    """Container for a single message from the Twitch chat.

    Instance variables:
    payload -- the message as a dict
    content -- the message text in lowercase
    original_content -- the message text in its original case
    username -- the Twitch user that sent the message
    Public methods:
    get_log_string
    get_log_webhook_payload
    """

    __slots__ = ('payload', 'content', 'original_content', 'username',)

    def __init__(self, payload: dict):
        """Initialise the class attributes.

        Takes the payload dict and makes it into an attribute, as well as some of its contents.
        """
        self.payload = payload
        self.content = payload['message'].lower()
        self.original_content = payload['message']
        self.username = payload['username'].lower().decode()

    def get_log_string(self) -> str:
        """Generate a string containing the message and the user who sent it in brackets."""
        return f'{self.original_content} ({self.username})'

    def get_log_webhook_payload(self) -> dict:
        """Generate a dict to be used as the payload of a Discord webhook.

        The generated dict will contain the username of the Twitch user who sent the message,
        the local time in H:M:S format, and a Discord embed containing the Twitch message with the title
        'Command event: '
        """
        lt = time.localtime()
        current_time = time.strftime('%H:%M:%S', lt)
        current_time_modded = f'Time: {current_time}'
        data = {
            'embeds': [
                {
                    'description': self.original_content,
                    'title': 'Command event:',
                },
            ],
            'username': self.username,
            'content': current_time_modded,
        }
        return data
