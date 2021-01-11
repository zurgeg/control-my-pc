python -m venv ".venv"
.venv\Scripts\activate.bat
python -m pip install -r "requirements.txt"
python "config\create_empty_config.py"
python "config\new_oauth_key.py"
echo "Please fill in the remaining fields of config\config.toml before running TwitchPlays.py."
