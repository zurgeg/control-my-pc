python -m venv ".venv"
source venv/bin/activate
python3 -m pip install -r "requirements.txt"
python3 "config\create_empty_config.py"
python3 "config\new_oauth_key.py"
echo "Please fill in the remaining fields of config\config.toml before running TwitchPlays.py."
