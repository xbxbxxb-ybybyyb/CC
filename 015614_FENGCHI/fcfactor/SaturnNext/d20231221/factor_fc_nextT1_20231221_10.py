# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
import numpy as np
s = FactorData()

def calc_mdd(_s):
    mdd = (np.maximum.accumulate(np.nancumsum(_s)) - np.nancumsum(_s)).max()
    return -mdd

def factor_fc_nextT1_20231221_10(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    def process(md_data):
        md_data.loc[md_data['pct_chg'] > 10, 'pct_chg'] = 10
        md_data.loc[md_data['pct_chg'] < -10, 'pct_chg'] = -10

        md_data['open'] = md_data['open'] * md_data['adjfactor']
        md_data['close'] = md_data['close'] * md_data['adjfactor']
        md_data['high'] = md_data['high'] * md_data['adjfactor']
        md_data['low'] = md_data['low'] * md_data['adjfactor']
        md_data['vwap'] = md_data['vwap'] * md_data['adjfactor']
        md_data['pre_close'] = md_data['pre_close'] * md_data['adjfactor']
        return md_data

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}
        # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -360)[0])
    md_data = IO.read_data([start_date_, end_date], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    process(md_data)

    md_data['c2v'] = (md_data['close'] - md_data['vwap']) / md_data['vwap']
    c2v_std = md_data['c2v'].unstack().rolling(10, min_periods=5).std().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = (md_data['c2v'] - c2v_std * 0.5).unstack().rolling(30, min_periods=1).median().stack()
    # ---------------------------------------------------------------------------------------------------------------------
    """
    close相对vwap涨跌幅滚动30日中位值
    25.25 -0.050
    =====>>>> 25.25 -0.05014817049258377 -0.005722058105571609 0.003867281232652801 skk_20231207_62，qyh_next_md_20231130_3 0.6233，0.589
    """
    return factor_df