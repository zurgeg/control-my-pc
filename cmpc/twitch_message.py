import time


class TwitchMessage(object):

    __slots__ = ('payload', 'content', 'original_content', 'username',)

    def __init__(self, payload:dict):
        self.payload = payload
        self.content = payload['message'].lower()
        self.original_content = payload['message']
        self.username = payload['username'].lower().decode()

    def get_log_string(self) -> str:
        return f"{self.original_content} ({self.username})"

    def get_log_webhook_payload(self) -> dict:
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
