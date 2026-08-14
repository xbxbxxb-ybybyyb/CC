# coding: utf-8
# Author：fengchi863
# Date ：2021/12/15 14:56

from ShortTermTrading.dataApi import getData, tradeDate, stockList
from xquant.factordata import FactorData
import pandas as pd, numpy as np
import talib
from abc import abstractmethod


class DailyTrendStockBase:
    def __init__(self, start_date, end_date):
        cal_start_date = tradeDate.get_pre_trade_date(start_date, 5)
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

        self.cal_date_list = cal_date_list
        self.date_list = date_list
        self.shift_start_date = cal_start_date
        self.start_date = start_date
        self.end_date = end_date
        self.stk_list = stk_list
        self.daily_st = daily_st
        self.daily_close_badj = daily_close_badj
        self.daily_pre_close_badj = daily_pre_close_badj
        self.daily_high_badj = daily_high_badj
        self.daily_low_badj = daily_low_badj
        self.daily_open_badj = daily_open_badj
        self.daily_pctchg = daily_pctchg
        self.daily_amt = daily_amt
        self.daily_limit_up = daily_limit_up
        self.daily_limit_down = daily_limit_down

    def index_cond(self):
        s = FactorData()
        index_data = s.get_factor_value(
            "WIND_AIndexEODPrices",
            s_info_windcode=['399005.SZ', '399001.SZ', '000001.SH'],
            factors=['s_info_windcode', 'trade_dt', 's_dq_close', 's_dq_open', 's_dq_amount'],
            trade_dt=self.date_list
        )
        date_list_str = list(map(str, self.date_list))
        index_close = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_CLOSE').loc[date_list_str]
        index_close.index = index_close.index.map(int)
        index_open = index_data.pivot('TRADE_DT', 'S_INFO_WINDCODE', 'S_DQ_OPEN').loc[date_list_str]
        index_open.index = index_open.index.map(int)
        index_ma5 = index_close.rolling(5).mean() < index_close
        ma5_sum = index_ma5.sum(axis=1)

        a1, a2, a3 = talib.MACD(np.array(index_close['000001.SH']), fastperiod=12, slowperiod=26, signalperiod=9)
        macd = pd.Series(a3, index=self.date_list)

        return (ma5_sum.shift(1) >= 2) & (macd.shift(1) > macd.shift(2))

    def st_cond(self):
        return self.daily_st

    @abstractmethod
    def concat_cond(self, *cond_list):
        pass
