import os
import webbrowser
from pathlib import Path

import requests
import toml

CONFIG_FOLDER = Path('config/')


# noinspection SpellCheckingInspection
def get_oauth_key(client_id='zvlttmj8jah002ucbqbpt1lkuq4oj3'):
    payload = {
        'client_id': client_id,
        'redirect_uri': 'https://cmpc.live/oauthdisplay',
        'response_type': 'token',
        'scope': 'chat:read'
    }

    url = requests.Request('GET', 'https://id.twitch.tv/oauth2/authorize', params=payload).prepare().url
    webbrowser.open(url)

    return input("OAuth key from page: ")


def save_oauth_key(oauth_key):
    # Set env var
    os.system(f'setx TWITCH_OAUTH_TOKEN "{oauth_key}"')

    # Edit config.toml
    config = toml.load(CONFIG_FOLDER / 'config.toml')
    config['twitch']['oauth_token'] = oauth_key
    toml.dump(config, CONFIG_FOLDER / 'config.toml')

    return True


if __name__ == '__main__':
    save_oauth_key(get_oauth_key())
