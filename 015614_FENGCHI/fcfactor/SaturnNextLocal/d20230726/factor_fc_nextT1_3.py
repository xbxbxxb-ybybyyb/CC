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

def factor_fc_nextT1_3(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD', 'minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    f_data = IO.read_data([s.tradingday(start_date, -10)[0], end_date], columns=['pre_close', 'open']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['ret1'] = np.log(f_data['open'] / f_data['pre_close'])
    close = IO.read_data([s.tradingday(start_date, -10)[0], end_date], columns=['m1330', 'm1430'], alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    f_data['ret2'] = close['m1430'] / close['m1330']
    close = IO.read_data([s.tradingday(start_date, -10)[0], end_date], columns=['m1000', 'm1125'], alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    f_data['ret3'] = close['m1125'] / close['m1000']
    f_data['factor'] = f_data['ret3'] * f_data['ret2']

    factor_df = pd.DataFrame(f_data['factor'].unstack().rolling(5, min_periods=1).sum().stack())
    factor_df.columns = [factor_name]
    # ----------------------------------------日内上午和下午涨跌幅之积，5日之和 9.75 -0.031 submit-------------------------------------------------------------------------
    return factor_df