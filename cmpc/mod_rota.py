import asyncio
import datetime

from cmpc.utils import send_webhook


ONE_DAY_DELTA = datetime.timedelta(days=1)


class ModRota:
    def __init__(self):
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
        now = datetime.datetime.utcnow()
        today = now.date()

        if last:
            sign = -1
        else:
            sign = 1

        for i in range(0, sign*7):
            day = today + ONE_DAY_DELTA * i
            rota_for_day = rota.get(self._day_name(day))
            if rota_for_day:
                rota_datetimes = [now]
                for rota_time in rota_for_day:
                    rota_time_parsed = datetime.datetime.strptime(rota_time, '%H:%M').time()
                    rota_datetime = datetime.datetime.combine(day, rota_time_parsed)
                    rota_datetimes.append(rota_datetime)

                rota_datetimes = sorted(rota_datetimes)
                try:
                    next_datetime = rota_datetimes[rota_datetimes.index(now) + sign]
                except IndexError:
                    pass
                else:
                    next_datetime_strf = next_datetime.strftime('%H:%M')
                    return rota_for_day[next_datetime_strf]

        return None
