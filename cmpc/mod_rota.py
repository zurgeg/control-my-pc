import asyncio
import datetime
import logging as log

from cmpc.utils import send_webhook


# todo: add docstrings
ONE_DAY_DELTA = datetime.timedelta(days=1)


class ModRota:
    def __init__(self, webhook_url, rota=None, discord_ids=None):
        self.webhook_url = webhook_url

        self.keep_running = False
        self.rota = {}
        self.download_rota()
        self.discord_ids = {}

    @staticmethod
    def _day_name(day):
        return day.strftime('%A')

    def download_rota(self):
        self.rota = {}

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
                         f"<@{mod_discord_id}> it's your turn to moderate the stream."
                         "If you can't, please ping another mod to get them to do it.")

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
