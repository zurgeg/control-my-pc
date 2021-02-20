# Changelog

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
