[More documentation in the central wiki.](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script)

# TwitchPlays

An overhaul update to DougDoug TwitchPlays script.

**This script is meant for twitch.tv/controlmypc / https://cmpc.live and its developers, you must have authentication from the development team or CMPC to run this script.**


# NOTICE: Any forks of this repo MUST be private. thank you.

# Installation:

  1) In order to run you must download python 3.xx (Will suggest latest version from here: https://www.python.org/downloads/).

  2) After downloading open a cmd and run these commands:
  
  * `python -m pip install --upgrade pip`
  * `python -m pip install -r requirements.txt`

  3)  Edit `config.toml` with your oauth and twitch token. (you can find your oauth token [here](http://twitchapps.com/tmi/)).       
  Set TWITCH_CHANNEL AND TWITCH_OAUTH_TOKEN environment variables if you want to use env vars, see For more information see [here](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script#how-to-set-environment-variables). 

  4)Run start.bat (And hope it doesn't crash cause it can't send data or can't authenticate account.)

## "I dont have all this fancy stuff, what can i do?"

NO API) If you do not have a api, leave these values blank and edit the manual configuration in `TwitchPlays.py` You mainly need `developer` as a admin, `moderator` is just at the minute for the `modsay ` command.

NO DISCORD) If you dont have a discord webhook, look at a guide online, if you dont want to do this, most of the dev commands wont be the best option for you, There is no error handling for no config at the minute, so your best bet is just to make a discord server and just use discord, NOTE: These do not need to be separate webhooks, they can all be the same (this is not recommended), but it would help if you dont want to make 6 webhooks.

NO TWITCH) If you are testing the script offline, you're fucked. There is no good way to do this at the minute, we might add a option in the future to do manual offline testing

# What's New:

Massive rewrite with improved code and new features.

## Full changelog:

- **vX.Y.Z YYYY-MM-DD INFO**
- **Date descending**
- v3.6.0 2020-11-xx Refactor connection to use `twitchio`, event-driven
- v3.5.0 2020-11-10 Add 'ptype' command, types by pasting to support unicode
- v3.4.0 2020-11-09 Add backup static dev list. Add more info to 'script online' discord webhook message.
- v3.4.1 2020-11-09 Fix unicode encode error in obs logging (type commands)
- v3.4.2 2020-11-09 Fix some mod commands that used the run dialog
- *Changelog created 2020-11-09*
- *Following entries are retroactive*
- v3.1.1 2020-10-31 Stable rewrite
- v3.0.0 2020-10-27 Rewrite
- v2.0.0 2020-07-25 Season 2
- v1.0.0 2020-07-17 Add new commands and obs logging
- v0.1.1 2020-06-11 Preserve capitalisation on type command
- v0.1.0 2020-06-10 First version on GitHub
