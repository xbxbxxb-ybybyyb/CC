# coding: utf-8
# Author：fengchi863
# Date ：2022/1/10 10:31

from ShortTermTrading.dataApi import getData, tradeDate, stockList
from xquant.factordata import FactorData
import pandas as pd, numpy as np
import talib
from abc import abstractmethod


class StockFilterBase:
    def __init__(self, start_date, end_date):
        cal_start_date = tradeDate.get_pre_trade_date(start_date, 250)
        cal_date_list = tradeDate.get_date_range(cal_start_date, end_date)
        date_list = tradeDate.get_date_range(start_date, end_date)
        daily_st = stockList.clean_stock_list(no_pause=False, no_ST=True, least_live_days=0,
                                              start_date=cal_start_date, end_date=end_date)
        stk_list = sorted(daily_st.columns.tolist())

        daily_close_badj = getData.get_daily_1factor('close_badj', code_list=stk_list, date_list=cal_date_list)
        daily_pre_close_badj = getData.get_daily_1factor('pre_close_badj', code_list=stk_list, date_list=cal_date_list)
        daily_high_badj = getData.get_daily_1factor('high_badj', code_list=stk_list, date_list=cal_date_list)
        daily_low_badj = getData.get_daily_1factor('low_badj', code_list=stk_list, date_list=cal_date_list)
        daily_open_badj = getData.get_daily_1factor('open_badj', code_list=stk_list, date_list=cal_date_list)
        daily_pctchg = getData.get_daily_1factor('pct_chg', code_list=stk_list, date_list=cal_date_list)
        daily_amt = getData.get_daily_1factor('amt', code_list=stk_list, date_list=cal_date_list)
        daily_limit_up = getData.get_daily_1factor('limit_up', code_list=stk_list, date_list=cal_date_list)
        daily_limit_down = getData.get_daily_1factor('limit_down', code_list=stk_list, date_list=cal_date_list)
        daily_live_days = getData.get_daily_1factor('live_days', code_list=stk_list, date_list=cal_date_list)

        self.cal_date_list = cal_date_list
        self.date_list = date_list
        self.cal_start_date = cal_start_date
        self.start_date = start_date
        self.end_date = end_date
        self.stk_list = stk_list
        self.daily_st = daily_st
        self.daily_close_badj = daily_close_badj
        self.daily_pre_close_badj = daily_pre_close_badj
        self.daily_high_badj = daily_high_badj
        self.daily_low_badj = daily_low_badj
        self.daily_open_badj = daily_open_badj
        self.daily_pctchg = daily_pctchg / 100
        self.daily_amt = daily_amt
        self.daily_limit_up = daily_limit_up
        self.daily_limit_down = daily_limit_down
        self.daily_live_days = daily_live_days
