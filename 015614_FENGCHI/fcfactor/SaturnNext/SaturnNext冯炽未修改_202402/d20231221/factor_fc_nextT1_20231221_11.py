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

def factor_fc_nextT1_20231221_11(start_date, end_date, IO, return_fillna_dic=False):
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
    c2v_std = md_data['c2v'].unstack().rolling(120, min_periods=5).std().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = (md_data['c2v'] - c2v_std * 3).unstack().rolling(20, min_periods=1).median().stack()
    # ---------------------------------------------------------------------------------------------------------------------
    """
    close-vwap 滚动20日中位值
    18.5 -0.040
    =====>>>> 18.5 -0.04014805441367578 -0.04144137487312147 0.016572495987910826 qyh_next_md_20231130_3，xbc_20230803_4 0.5307，0.5258
    """
    return factor_df