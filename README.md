[More documentation in the central wiki.](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script)

# Twitch-Plays-Control-My-PC

An overhaul update to DougDoug TwitchPlays script.

**This script is meant for twitch.tv/controlmypc / https://cmpc.live and its developers, you must have authentication from the development team or CMPC to run this script.**


# NOTICE: Any forks of this repo MUST be private. thank you.

# Installation:

  1) In order to run you must download python 3.xx (Will suggest latest version from here: https://www.python.org/downloads/).

  2) After downloading open a cmd and run these commands:
  
  * `python -m pip install --upgrade pip`
  * `python -m pip install -r requirements.txt`

  3) Set TWITCH_CHANNEL AND TWITCH_OAUTH_TOKEN environment variables (you can find your oauth token [here](http://twitchapps.com/tmi/)).    
  For more information see the [documentation](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script#how-to-set-environment-variables).    
  Alternately you can use the legacy option and edit `config.toml` with the username and oauth.

  4)Run start.bat (And hope it doesn't crash cause it can't send data or can't authenticate account.)

# What's New:

Massive rewrite with improved code and new features.
