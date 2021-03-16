import json
import time
import logging as log

import requests
from cmpc.utils import send_webhook


class CmpcApi:
    def __init__(self, config):
        self.config = config

    # todo: update docstrings
    def get_json_from_api(self, url, static_backup_path, force_static=False):
        """Init a cmpc.Permissions object after retrieving source dev and mod lists.

        Args:
            url -- the url to attempt to retrieve JSON from
            static_backup_path -- path to the static backup local JSON file
        Returns:
            a cmpc.Permissions object generated with load_user_permissions
        If retrieval from the url is successful, it will be backed up to the local file.
        Otherwise, if retrieval is unsuccessful, the local file will be used instead, and warnings will be logged.
        The warnings include information about when the local file was updated and retrieved.
        """
        # Attempt get dev and mod lists from API.
        log.info(f'[API] Requesting data! ({url})')
        try:
            if force_static:
                log.warning('Forcing getting from static backup instead of api.')
                raise requests.RequestException

            api_response = requests.get(url)
            if not api_response.ok:
                raise requests.RequestException
            else:
                api_json = api_response.json()
                log.debug('[API] Data here, and parsed!')

                # Save retrieved JSON to backup
                with open(static_backup_path, 'w') as static_backup_file:
                    json.dump(api_json, static_backup_file)
                log.debug('[API] Backed up to static backup file')

        # If the request errored or response status code wasn't 200 'ok', use backup
        except (requests.RequestException, json.JSONDecodeError):
            log.warning('[API] Failed to load data from API')
            with open(static_backup_path, 'r') as static_backup_file:
                api_json = json.load(static_backup_file)

            log.info('[API] Loaded lists from static file instead')
            retrieved_time = time.strftime('%Y-%m-%dT%H:%M', time.gmtime(static_backup_path.stat().st_mtime))
            try:
                log.warning('[API] One or multiple lists may be unavailable or incomplete/out of date\n'
                            f"    JSON last updated: {api_json['last_updated']}\n"
                            f"    Retrieved: {retrieved_time}")
                # noinspection PyUnboundLocalVariable
                send_webhook(self.config['discord']['systemlog'],
                             'Failed to load data from API\n'
                             'Loaded dev list from static file instead\n'
                             'One or multiple lists may be unavailable or incomplete/out of date\n'
                             f"Last updated: {api_json['last_updated']}\n"
                             f"Retrieved: {retrieved_time}\n\n"
                             f"[***Stream Link***](<https://twitch.tv/{self.config['twitch']['username']}>)\n"
                             "**Environment -** {config['options']['DEPLOY']}\n"
                             f"**Response Status Code- ** {api_response.status_code}"
                             )
            except TypeError:
                log.warning('Your apiconfig backup is out of date and missing some fields. Trying to run anyway.')

        return api_json
