import time


class TwitchMessage:
    """Container for a single message from the Twitch chat.

    Instance variables:
        content -- the message text in lowercase
        original_content -- the message text in its original case
        username -- the Twitch user that sent the message
        original_username -- the Twitch user that sent the message in original case
    Public methods:
        get_log_string
        get_log_webhook_payload
    """

    __slots__ = ('content', 'original_content', 'username', 'original_username',)

    def __init__(self, message_content, message_author):
        """Initialise the class attributes.

        Takes the capitalised message content and author and makes them into attributes.
        """
        self.content = message_content.lower()
        self.original_content = message_content
        self.username = message_author.lower()
        self.original_username = message_author

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
