# coding: utf-8
# Author：fengchi863
# Date ：2023/4/6 14:27

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_dis_pct_ma5(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_dis_pct_ma5'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -10)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['amt', 'pct_chg', 'open', 'close', 'high', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['open'] = md_data['open'] * md_data['adjfactor']
    md_data['close'] = md_data['close'] * md_data['adjfactor']
    md_data['high'] = md_data['high'] * md_data['adjfactor']

    md_data['ma5'] = md_data['close'].unstack().rolling(5).mean().stack()
    md_data['dis_pct_ma5'] = md_data['close'] / md_data['ma5'] - 1

    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['dis_pct_ma5']
    return factor_df