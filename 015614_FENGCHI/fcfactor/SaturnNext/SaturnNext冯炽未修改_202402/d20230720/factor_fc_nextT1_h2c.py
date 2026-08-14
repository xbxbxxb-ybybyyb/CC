# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_nextT1_h2c(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -10)[0])  # 向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_, end_date], columns=['pct_chg', 'high', 'close'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['h2c'] = md_data['high'] / md_data['close'] - 1
    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['h2c'].unstack().rolling(5, min_periods=3).mean().stack()
    # ------------------------------------------最高价比最低价滚动5日均值--19.42 3.94-----------------------------------------------------------------------
    return factor_df