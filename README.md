[More documentation in the central wiki.](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script)

# TwitchPlays

An overhaul update to DougDoug TwitchPlays script.

**This script is meant for twitch.tv/controlmypc / https://cmpc.live and its developers, you must have authentication from the development team or CMPC to run this script.**


# NOTICE: Any forks of this repo MUST be private. thank you.

# Installation:

  (Note: It is recommended that you know how to use the Terminal of your OS and that you have basic knowledge of the Git CLI.)

  1) In order to run you must download Python 3.9 (https://www.python.org/downloads/).

  2) To install you can either do one of 2 things.
    - Clone using Git
    - Download the Zip file

  3) After downloading open a terminal of your choice,  and run these commands:
  
  * `python -m pip install --upgrade pip`
  * `python -m pip install -r requirements.txt`

  4)  Edit `config.toml` with your oauth and twitch token. (you can get an oauth token with `new_oauth_key.py`).       
  Set TWITCH_CHANNEL AND TWITCH_OAUTH_TOKEN environment variables if you want to use env vars, see For more information see [here](https://gitlab.com/controlmypc/docs/-/wikis/documentation/Script#how-to-set-environment-variables). 

  5) Run `TwitchPlays.py` using `python TwitchPlays.py

## "I don't have all this fancy stuff, what can i do?"

- No API ) If you don't have a Webserver or CDN hosting your config, you can modify `TwitchPlays.py (Line 137)` to use a static user list.

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

- No Webhooks) If you don't know how to make a discord webhook, there are plenty of guides online. Without a webhook most commands di=o absolutely nothing. If you would like to send webhooks to a different service (I.E: Slack), you can modify some of the webhook code (`./cmpc/utils.py` handles most webhooks.). You can use 1 webhook for the entire script, but it is not recommended.

- Offline / No Twitch) If you are running the script without Twitch and/or you are offline, sadly the script will not function. We are planning on adding a feature to test offline without the use of Twitch and/or Webhooks.

## Script change Highlights:

Massive rewrite with improved code and new features.

## Full changelog:

- **vX.Y.Z YYYY-MM-DD INFO**
- **Date descending**
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
