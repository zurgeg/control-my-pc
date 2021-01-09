[More documentation in the central wiki.](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script)

# TwitchPlays

The script that allows controlling of a pc remotely through a Twitch chat. Started as an overhaul update to DougDoug TwitchPlays script.

**This script is meant for twitch.tv/controlmypc / https://cmpc.live and its developers, you must have authentorisation from the development team or CMPC to run this script.**


# NOTICE: Any forks of this repo MUST be private. thank you.

# Installation:

  1) In order to run you must download python 3.x.x (Will suggest latest version from here: https://www.python.org/downloads).
     The recommended version is in [runtime.txt](https://gitlab.com/controlmypc/TwitchPlays/-/blob/master/runtime.txt) in the [heroku style](https://devcenter.heroku.com/articles/python-runtimes), and most testing is done on 3.9 and 3.8, but all versions of python 3 should be supported in theory - if you find a bug, please report it.

  2) Install the dependences (using a (virtualenv)[https://docs.python.org/3/tutorial/venv.html] or other virtual environment can be a good idea):
  
  * `python -m pip install --upgrade pip`
  * `python -m pip install --upgrade wheel`
  * `python -m pip install -r requirements.txt`

  3) Create `config/config.toml` based on `config/config.example.toml` with your Twitch username, oauth key, and other info and settings. (you can generate a blank config.toml with `config/create_empty_config.py` and get a Twitch oauth token with `new_oauth_key.py`).

  4) Run TwitchPlays.py - you can dp this as a command on most environments as `TwitchPlays`.

## "I don't have all this fancy stuff (Discord webhooks, API for moderator lists, etc.), what can I do?"

NO API) If you do not have a api, leave these values blank and edit the manual configuration in `TwitchPlays.py` You mainly need `developer` as an admin, `moderator` and moderator for the `modsay` command (haha jk no one uses that) and moderation features - script banning and approving.    
We should make this feature optional, or create a stripped down version.

NO DISCORD) If you don't have a discord webhook, look at a guide online. A discord webhook is just a link that allows messages to be sent to a discord channel by a program. If you don't want to do this, most of the dev commands won't work, and there may be uncaught errors. NOTE: These do not need to be separate webhooks, they can all be the same (this is not recommended), but it would help if you don't want to make 6 webhooks.

NO TWITCH) If you are testing the script offline, you're fucked. There is no good way to do this at the minute, we might add a option in the future to do manual offline testing

# What's New highlight:

Moderation features to ignore brand-new user accounts and allow banning only for the script, withotu banning from Twitch chat.

## Full changelog:
*This will likely be moved to its own file.*

- **vX.Y.Z YYYY-MM-DD INFO**
- **Date descending**
- v3.8.0 2020-12-21 Add new moderation features for ignoring brand-new user accounts and script-banning users  
- v3.7.1 2020-12-11 Fix error handling for go to command  
- v3.7.0 2020-12-04 Remove environment variable support for simplicity's sake, add !modalert ping role ID in config.
- v3.6.0 2020-11-22 Refactor connection to use `twitchio`, event-driven. Also improve a ton of code with refactoring, and some minor changes like new commands.
- v3.5.1 2020-11-14 Make hold key functionality work in more games (was broken in rewrite).
- v3.5.0 2020-11-10 Add 'ptype' command, types by pasting to support unicode
- v3.4.2 2020-11-09 Fix some mod commands that used the run dialog
- v3.4.1 2020-11-09 Fix unicode encode error in obs logging (type commands)
- v3.4.0 2020-11-09 Add backup static dev list. Add more info to 'script online' discord webhook message.
- *Changelog created 2020-11-09*
- *Following entries are retroactive*
- v3.1.1 2020-10-31 Stable rewrite
- v3.0.0 2020-10-27 Rewrite
- v2.0.0 2020-07-25 Season 2
- v1.0.0 2020-07-17 Add new commands and obs logging
- v0.1.1 2020-06-11 Preserve capitalisation on type command
- v0.1.0 2020-06-10 First version on GitHub
