# coding: utf-8
# Author：fengchi863
# Date ：2021/1/20 14:03

'''
卖出端暂时还不需要设计成盘中实时监控
'''

from ShortTermTrading.dataApi.stockList import clean_stock_list, trans_int2windcode
from ShortTermTrading.dataApi.tradeDate import get_date_range, get_pre_trade_date
from ShortTermTrading.dataApi.getData import get_daily_1factor, get_minute_1factor, get_daily_1day
from ShortTermTrading.Util.tools import *
from ShortTermTrading.ConceptApi.ConceptApi import get_concept_values
from ShortTermTrading.interface.ActiveConceptApi import get_active_stock_1concept
from ShortTermTrading.Util.System import fetch_man_made_monitor_list, check_shape
from xquant.thirdpartydata.marketdata import MarketData
import pandas as pd, numpy as np
from ShortTermTrading.conf.path_conf import daily_monitor_path, man_made_concept_data_path
from tqdm import tqdm
from multiprocessing import Pool
import time

class SellMonitor:

    def __init__(self, start_date=20200101, end_date=20201231):
        shift_start_date = get_pre_trade_date(start_date, 30)
        shift_end_date = get_pre_trade_date(end_date, 5)
        date_list = get_date_range(shift_start_date, end_date)
        daily_st = clean_stock_list(no_pause=False, no_ST=True, least_live_days=0, start_date=shift_start_date, end_date=end_date)
        stk_list = sorted(daily_st.columns.tolist())

        daily_close_badj = get_daily_1factor('close_badj', code_list=stk_list, date_list=date_list)
        daily_pre_close_badj = get_daily_1factor('pre_close_badj', code_list=stk_list, date_list=date_list)
        daily_high_badj = get_daily_1factor('high_badj', code_list=stk_list, date_list=date_list)
        daily_low_badj = get_daily_1factor('low_badj', code_list=stk_list, date_list=date_list)
        daily_swing = get_daily_1factor('swing', code_list=stk_list, date_list=date_list)
        daily_open_badj = get_daily_1factor('open_badj', code_list=stk_list, date_list=date_list)
        daily_pctchg = get_daily_1factor('pct_chg', code_list=stk_list, date_list=date_list)
        daily_amt = get_daily_1factor('amt', code_list=stk_list, date_list=date_list)
        daily_turn = get_daily_1factor('turn', code_list=stk_list, date_list=date_list)

        intra_minute_amt = get_minute_1factor('amt', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_close_badj = get_minute_1factor('close_badj', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)
        intra_minute_close_nbadj = get_minute_1factor('close', start_datetime=shift_start_date, end_datetime=end_date,
                                            code_list=stk_list)

    def start_intra(self):
        pass

if __name__ == '__main__':
    sl = SellMonitor()
    holding_list = []
    sl.start_intra()