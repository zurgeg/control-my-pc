import setuptools

import TwitchPlays


with open('README.md', 'r', encoding='utf-8') as readme_file:
    long_description = readme_file.read()

setuptools.setup(
    name='cmpc-twitchplays',
    version=TwitchPlays.__version__,
    author='CMPC Developers',
    author_email='controlmypc505@gmail.com',
    description='The script that allows controlling of a pc remotely through a Twitch chat. '
                'Started as an overhaul update to DougDoug TwitchPlays script.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://gitlab.com/controlmypc/TwitchPlays',
    packages=['cmpc'],
    py_modules=['TwitchPlays', 'config/create_empty_config', 'config/new_oauth_key'],
    entry_points={
        'console_scripts': [
            'cmpc-twitchplays=twitchplays'
        ]
    },
    data_files=[
        ('config', 'config/config.example.toml'),
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: Other/Proprietary License',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS',
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: AsyncIO',
        'Natural Language :: English',
    ],
    python_requires='>=3',
    install_requires=[
        'PyAutoGUI',
        'PyDirectInput',
        'twitchio'
    ]
)
