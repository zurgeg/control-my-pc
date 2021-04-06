import asyncio
import datetime
import logging as log
from pathlib import Path

import twitchio
import cmpc.api_requests
import cmpc.permission_handler
from cmpc.utils import send_webhook


# todo: add docstrings
ONE_DAY_DELTA = datetime.timedelta(days=1)
CONFIG_FOLDER = Path('config/')


class ModRota:
    def __init__(self, bot, mod_presence_check_interval_minutes=10, rota=None, discord_ids=None):
        self.bot = bot
        self.mod_presence_check_interval_seconds = mod_presence_check_interval_minutes * 60
        self.channel_to_check = self.bot.config['twitch']['channel_to_join']
        self.webhook_url = self.bot.config['discord']['rota_reminders']
        self.rota_url = self.bot.config['api']['mod_rota']
        self.discord_ids_url = self.bot.config['api']['discord_ids']

        self.keep_running = False
        self.keep_running_mod_presence_checks = False
        self.api_requests = cmpc.api_requests.CmpcApi(self.bot.config)
        if rota is None:
            self.rota = {}
            self.download_rota()
        if discord_ids is None:
            self.discord_ids = {}
            self.download_discord_ids()

    @staticmethod
    def _day_name(day):
        return day.strftime('%A')

    def download_rota(self):
        json_response = self.api_requests.get_json_from_api(url=self.rota_url,
                                                            static_backup_path=CONFIG_FOLDER/'rota.json')
        self.rota = json_response['rota']

    def download_discord_ids(self):
        json_response = self.api_requests.get_json_from_api(url=self.discord_ids_url,
                                                            static_backup_path=CONFIG_FOLDER / 'discord.json')
        self.discord_ids = json_response['discord_ids']

    def next_on_duty(self, rota=None, last=False):
        if rota is None:
            rota = self.rota
        if not rota:
            log.error('[ROTA] Rota is empty.')
            return None, None

        now = datetime.datetime.utcnow()
        today = now.date()

        if last:
            sign = -1
        else:
            sign = 1

        # iterate over the next seven days
        # (or the last seven days if 'last' is True)
        for i in range(0, sign*7):
            day = today + ONE_DAY_DELTA * i
            rota_for_day = rota.get(self._day_name(day))
            if rota_for_day:
                # create a datetime for each rota hh:mm within the day
                rota_datetimes = [now]
                for rota_time in rota_for_day:
                    rota_time_parsed = datetime.datetime.strptime(rota_time, '%H:%M').time()
                    rota_datetime = datetime.datetime.combine(day, rota_time_parsed)
                    rota_datetimes.append(rota_datetime)

                # try to get the datetime immediately before or after the current real time
                rota_datetimes = sorted(rota_datetimes)
                try:
                    next_datetime = rota_datetimes[rota_datetimes.index(now) + sign]
                except IndexError:
                    pass
                else:
                    # if we got it return it
                    next_datetime_strf = next_datetime.strftime('%H:%M')
                    return next_datetime, rota_for_day[next_datetime_strf]

        return None, None

    def send_reminder_ping(self, twitch_mod, discord_ids=None):
        if discord_ids is None:
            discord_ids = self.discord_ids

        try:
            mod_discord_id = discord_ids[twitch_mod]
        except KeyError:
            log.error(f"[ROTA] It's this mod's turn on the rota, but their discord id was not found: {twitch_mod}")
        else:
            send_webhook(self.webhook_url,
                         f"<@{mod_discord_id}> it's your turn to moderate the stream. "
                         f'<https://www.twitch.tv/{self.channel_to_check}>\n'
                         "If you can't, please ping another mod to get them to do it.")

    async def mod_presence_check(self):
        try:
            chatters = await self.bot.get_chatters(self.channel_to_check)
        except twitchio.errors.HTTPException:
            log.error('Unable to get chatters list for channel in mod presence check.')
            return False

        for user in chatters.moderators+chatters.broadcaster:
            user_permissions = self.bot.user_permissions_handler.get(user, cmpc.Permissions())
            if user_permissions.moderator or user_permissions.developer:
                return True

        return False

    async def run_mod_presence_checks(self):
        self.keep_running_mod_presence_checks = True
        while self.keep_running_mod_presence_checks:
            mods_present = await self.mod_presence_check()
            if not mods_present:
                cmpc.send_webhook(self.webhook_url,
                                  f"{self.bot.config['discord']['modalertping']} "
                                  'there are currently no mods on the stream! '
                                  f'<https://www.twitch.tv/{self.channel_to_check}>')

            await asyncio.sleep(self.mod_presence_check_interval_seconds)

    async def run(self):
        self.keep_running = True

        while self.keep_running:
            next_datetime, next_mod = self.next_on_duty()
            if next_datetime is None or next_mod is None:
                log.error("[ROTA] Couldn't get the next mod on duty from the rota. Stopping rota reminders.")
                self.keep_running = False
                return

            time_till_next = (next_datetime - datetime.datetime.utcnow()).total_seconds()
            next_datetime_strf = next_datetime.strftime('%A %d %b %H:%M')
            log.info(f'[ROTA] Next mod on duty: {next_mod} at {next_datetime_strf}.')
            log.info(f'[ROTA] Rota pausing for {int(time_till_next)} seconds.')

            await asyncio.sleep(time_till_next)
            self.send_reminder_ping(next_mod)
