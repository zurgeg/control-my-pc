# Changelog

## [3.32.1] - 2021-04-15
### added
- warn if not running as admin
- send a warning webhook to the moderators when an account is ignored

## [3.32.0] - 2021-04-06 - 'Season 3 Day One Patch'
### added
- back and forwards commands
- reload as an alias of refresh
- backspace {n} command presses backspace n times
- stream link in rota reminders
- twitch messages sent by the script will start with \[SCRIPT\]
### fixed
- alt {n} tab will no longer work if you write anything after tab
- handle too large arguments for go to and drag to without erroring
- argument for the type command will be processed properly with different capitalisations of `type`
- new user cache system actually works

## [3.31.0] - 2021-03-12
### added
- Connect to OBS with websockets, as an alternative to executing.txt
### changed
- Small refactor to make command logging its own file
- Major refactor to make moderation features its own file, then switch the cache to an sqlite db.

## [3.30.0] - 2021-02-25
### versioning change
The version number jumped to 3.30 to indicate the start of Season 3. This version was formerly v4.0.0, but we chose this instead, so the version number would match the season number.
### added
- Moderation rota reminder system
- Multi alt-tab
### fixed
- Use twitchio's twitch api endpoint access, delete our old function

## [3.10.0] - 2021-02-20
### added
- Give the `TwitchPlays` class a random ID which you can get using the `../script id` command, and use to stop a specific instance using the `../script stop <id>` command.
### fixed
- Error handling for the `drag to` command.

## [3.9.0] - 2021-01-21
### added
- New offline mode feature using the startup flag `--offline-mode`

## [3.8.0] - 2020-12-21
### added
- New moderation features
    - Ignore commands from users whose accounts are under a certain age
    - Manually approve users even if their accounts are under the required age
    - Ban, unban, timeout, and untimeout users on a script level, so they can still chat but can't run commands
    - Caching of user info in JSON format to make all of the above features work faster.

## [3.7.0] - 2020-12-04
### added
- !modalert ping role ID in config.
### removed
- Environment variable support has been removed for simplicity's sake since the active `config.toml` is now in the gitignore, and we have `config.example.toml`.
- `alt f4` is no longer an alias for the `quit` command due to moderator feedback.
### fixed
- `drag to` command is back

## [3.6.0] - 2020-11-22 - 'event-driven-connection'
### added
- Some minor changes like new commands.
### changed
- Refactor connection to use `twitchio`, event-driven.
- Also improve a ton of code with refactoring.
### fixed
- Make hold key functionality work in more games (was broken in rewrite).

## [3.5.0] - 2020-11-10
### added
- Add 'ptype' command, types by pasting to support unicode
### fixed
- Fix some mod commands that used the run dialog
- Fix unicode encode error in obs logging (type commands)

## [3.4.0] - 2020-11-09
### added
- Add backup static dev list.
- Create changelog in readme.
### changed
- Add more info to 'script online' discord webhook message.



Entries after this point are retroactive.

## [3.1.1] - 2020-10-31 - 'Stable rewrite'

## [2.0.0] - 2020-07-25 - 'Season 2'

## [1.0.0] - 2020-07-17 - 'old-script'
### added 
- New commands
- obs logging.
