@echo off

:: This variable should be the path to the intro video
set intro="intro.mp4"
:: Play the intro in vlc fullscreen then close
:: Ensure before running that vlc is installed and added to PATH
vlc -f --no-osd --no-play-and-pause %intro% vlc://quit

:loop
python TwitchPlays.py
goto loop
