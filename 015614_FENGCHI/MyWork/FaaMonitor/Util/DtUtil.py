# coding: utf-8
# Author：fengchi863
# Date ：2021/5/27 8:42

import datetime as dt
from FaaMonitor.dataApi import tradeDate
from FaaMonitor.dataApi.tradeDate import trade_minutes

class DtUtil:
    def __init__(self):
        pass

    @staticmethod
    def get_today_date():
        return int(dt.datetime.today().strftime('%Y%m%d'))

    def get_yesterday_date(self):
        today_date = self.get_today_date()
        return tradeDate.get_pre_trade_date(today_date)

    @staticmethod
    def get_now_hm():
        return int(dt.datetime.today().strftime('%H%M'))

    @staticmethod
    def get_standard_YmdHM():
        return dt.datetime.today().strftime('%Y-%m-%d %H:%M')

    @staticmethod
    def get_pre_minute(time: int, lag: int):
        if 1130 <= time < 1300:
            time = 1129
        idx = trade_minutes.index(time)
        if idx - lag <= 0:
            return 930
        elif idx - lag >= len(trade_minutes):
            return 1500
        else:
            return trade_minutes[idx - lag]

    @staticmethod
    def get_standard_HMS(delta=0):
        if delta == 0:
            return dt.datetime.today().strftime('%H:%M:%S')
        else:
            return (dt.datetime.today() + dt.timedelta(minutes=delta)).strftime('%H:%M:%S')

DtUtil = DtUtil()