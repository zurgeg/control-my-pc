#!/usr/bin/env python

"""Script to authorise our Twitch app to get an oauth key to use with the main script.

If you just want to get the key, simply exit the program after you get it. If you want it to automatically save the key,
input it. Note that it's preferred to add oauth: to the start if you're going to save them manually.
I'll probably improve the script and make this simpler.

Files:
    config/config.toml -- where the new key will be assigned to
"""

import os
import webbrowser
from pathlib import Path

import requests
import toml

CONFIG_FOLDER = Path('config/')


# noinspection SpellCheckingInspection
def get_oauth_key(client_id='zvlttmj8jah002ucbqbpt1lkuq4oj3', scope='chat:read'):
    """Open a browser window to get a Twitch oauthkey, ask the user to input the key, and return it formatted."""
    payload = {
        'client_id': client_id,
        'redirect_uri': 'https://cmpc.live/oauthdisplay',
        'response_type': 'token',
        'scope': scope
    }

    url = requests.Request('GET', 'https://id.twitch.tv/oauth2/authorize', params=payload).prepare().url
    webbrowser.open(url)

    oauthraw = input("OAuth key from page: ")
    if not oauthraw.startswith('oauth:'):
        oauth = f'oauth:{oauthraw}'

    return oauth


def save_oauth_key(oauth_key):
    """Save an oauth key to the config.toml."""

    # Edit config.toml
    config = toml.load(CONFIG_FOLDER/'config.toml')
    config['twitch']['oauth_token'] = oauth_key
    with open(CONFIG_FOLDER / 'config.toml', 'w') as config_file:
        toml.dump(config, config_file)

    # Ask them if they want to set a env var
    cheese = input("[Y/N] Save as a env var?")
    if cheese.lower() == "y":
        print("Cheese.")
        os.system(f'setx TWITCH_OAUTH_TOKEN "{oauth_key}"')
    if cheese.lower() == "n":
        pass # do nothing
    return True


if __name__ == '__main__':
    save_oauth_key(get_oauth_key())
