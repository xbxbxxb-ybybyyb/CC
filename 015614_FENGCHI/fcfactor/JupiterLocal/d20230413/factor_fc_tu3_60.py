# coding: utf-8
# Author：fengchi863
# Date ：2023/4/13 21:43

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_tu3_60(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_tu3_60'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -250)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['turn'], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    turn_flag = md_data['turn'].unstack() > 3
    ret = turn_flag.rolling(60).sum().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = ret
    return factor_df