# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 14:30

import pandas as pd
import numpy as np
import decimal
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_dis_ma_5_10(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_dis_ma_5_10'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -15)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['amt', 'pct_chg', 'open', 'close', 'high', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['open'] = md_data['open'] * md_data['adjfactor']
    md_data['close'] = md_data['close'] * md_data['adjfactor']

    md_data['ma5'] = md_data['close'].unstack().rolling(5).mean().stack()
    md_data['ma10'] = md_data['close'].unstack().rolling(10).mean().stack()
    md_data['dis_ma_5_10'] = md_data['ma5'] / md_data['ma10'] - 1

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['dis_ma_5_10']
    return factor_df
