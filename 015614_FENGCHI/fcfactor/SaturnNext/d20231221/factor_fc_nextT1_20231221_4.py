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

def factor_fc_nextT1_20231221_4(start_date, end_date, IO, return_fillna_dic=False):
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
    c2v_std = md_data['c2v'].unstack().rolling(20, min_periods=5).std().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = (md_data['c2v'] - c2v_std).unstack().rolling(6, min_periods=1).median().stack()
    # ---------------------------------------------------------------------------------------------------------------------
    """
    20日均线与黄线距离计算多日平均
    50.208 -0.082 
    =====>>>> 50.208333333333336 -0.08229968471740398 -0.011091255056991512 0.009778995098181975 qyh_next_md_20231130_3，qyh_md_amt_5_20 0.6484，0.55
    """
    return factor_df