# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_nextT1_1(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -30)[0])  #向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_,end_date],columns = ['pct_chg']
                           ,alt = '/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data.loc[md_data['pct_chg'] > 10, 'pct_chg'] = 10
    md_data.loc[md_data['pct_chg'] < -10, 'pct_chg'] = -10
    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['pct_chg'].unstack().rolling(20,min_periods=3).std().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return factor_df