# coding: utf-8
# Author：fengchi863
# Date ：2023/3/30 15:43

import pandas as pd
import numpy as np
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_up_pct_3d_mean(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='fc_up_pct_3d_mean'

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}

    start_date_ = int(s.tradingday(str(start_date), -10)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['close', 'high', 'open', 'pre_close', 'adjfactor']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data.loc[:, 'close'] = md_data['close'] * md_data['adjfactor']
    md_data.loc[:, 'high'] = md_data['high'] * md_data['adjfactor']
    md_data.loc[:, 'open'] = md_data['open'] * md_data['adjfactor']
    md_data.loc[:, 'pre_close'] = md_data['pre_close'] * md_data['adjfactor']

    md_data['stock_code'] = md_data.index.get_level_values(1)
    md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    md_data['ret'] = (md_data['high'] - md_data[['open', 'close']].max(axis=1)) / md_data['pre_close']
    md_data.loc[(md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'ret'] = md_data.loc[
                                                                                                            (md_data['stock_code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'ret'] / 2
    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['ret'].unstack().rolling(5, min_periods=3).sum().stack()
    return factor_df