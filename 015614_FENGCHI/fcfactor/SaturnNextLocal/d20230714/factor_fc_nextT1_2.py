# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_nextT1_2(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -60)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['pct_chg', 'high', 'close'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['h2c'] = md_data['high'] / md_data['close'] - 1
    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['h2c'].unstack().rolling(10, min_periods=3).mean().stack() / md_data['h2c'].unstack().rolling(5, min_periods=3).mean().stack()
    # --------------------------------------------------------------------------4.79 -2.04-----------------------------------------
    return factor_df