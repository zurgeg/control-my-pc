#!/usr/bin/env python

"""Create an empty config.toml file based on config.example.toml, for you to fill in the empty fields.

This script should aid easy setup. If config.toml already exists, it will ask before overwriting.
"""

import os
import sys
import toml


# todo: test
# todo: add support for command line options e.g. skip overwrite warning
# todo: better code structure - functions pls


# Load example
try:
    example_config = toml.load('config.example.toml')
except FileNotFoundError:
    print('config.example.toml not found, exiting.')
    sys.exit(1)

# Check new doesn't already exist
if os.path.exists('config.toml'):
    choice = input('config.toml already exists, do you want to overwrite it? y/N\n')
    if choice.lower() != 'y':
        sys.exit(2)

# Generate config with empty values, except for keys under 'options' which have working values in the example file.
config = {}
for toplevel_key, subkeys in example_config.items():
    if toplevel_key == 'options':
        config['options'] = example_config['options']
    else:
        for subkey, value in subkeys.items():
            config[toplevel_key] = {}
            config[toplevel_key][subkey] = type(value)()

# Save new config file
with open('w', 'config.toml') as new_config_file:
    toml.dump(config, new_config_file)
