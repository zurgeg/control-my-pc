[More documentation in the central wiki.](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script)

# TwitchPlays

The script that allows controlling of a pc remotely through a Twitch chat. Started as an overhaul update to DougDoug TwitchPlays script.


**This script is meant for twitch.tv/controlmypc / https://cmpc.live, you must have authorisation from controlmypc to run this script.**


# NOTICE: Any forks of this repo MUST be private. thank you.

# Installation:

  (Note: It is recommended that you know how to use the Terminal of your OS and that you have basic knowledge of the Git CLI.)

  1) In order to run you must download a 3.X.X version of Python (https://www.python.org/downloads/). The script is normally ran on python version `3.8` - `3.9`. The current recommended python version [runtime.txt](https://gitlab.com/controlmypc/TwitchPlays/-/blob/master/runtime.txt) using the [heroku style](https://devcenter.heroku.com/articles/python-runtimes).

  2) To install you can either do one of 2 things.
  - Clone using Git
  - Download the Zip file

  3) After downloading open a terminal of your choice, and run these commands to install the script's dependencies (using a [virtualenv](https://docs.python.org/3/tutorial/venv.html) or other virtual environment can be a good idea)::
  
  * `python -m pip install --upgrade pip wheel`
  * `python -m pip install -r requirements.txt`

  4)  Create `config/config.toml` based on `config/config.example.toml` with your Twitch username, oauth key, and other info and settings. (you can generate a blank config.toml with `config/create_empty_config.py` and get a Twitch oauth token with `new_oauth_key.py`).

  5) Run `TwitchPlays.py` using `python TwitchPlays.py` - You can do this as a command on most environments as `TwitchPlays`.

## "I don't have all this fancy stuff (Discord webhooks, API for moderator lists, etc.), what can i do?"

- No API ) If you don't have a Webserver or CDN hosting your config, you can modify `TwitchPlays.py (Line 137)` to use a static user list. Leaving out config values is a wanted feature and may be added in the future

Example static user list.
```
{
  "devlist" : [
    "developers here"
  ],
  "modlist" : [
    "moderators here"
  ]
}

```

- No Webhooks) If you don't know how to make a discord webhook, there are plenty of guides online. Without a webhook most commands do absolutely nothing. If you would like to send webhooks to a different service (I.E: Slack), you can modify some of the webhook code (`./cmpc/utils.py` handles most webhooks.). You can use 1 webhook for the entire script, but it is not recommended.

- Offline / No Twitch) If you are running the script without Twitch and/or you are offline, you can start the script in offline only mode. Do this by adding the `--offline-mode` flag to your start command.

# What's New highlight:

Moderation features to ignore brand-new user accounts and allow banning only for the script, without banning from Twitch chat.

## Full changelog:
*This will likely be moved to its own file.*

- **vX.Y.Z YYYY-MM-DD INFO**
- **Date descending**
- v3.9.0 2021-1-21 New offline mode feature using the startup flag `--offline-mode`
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
