# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
import numpy as np
s = FactorData()

def factor_fc_nextT1_6(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    f_data = IO.read_data([s.tradingday(start_date, -10)[0], end_date], columns=['vwap', 'close', 'volume']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['c2v'] = f_data['close'] / f_data['vwap']
    f_data.loc[f_data[f_data['volume'] == 0].index, 'c2v'] = np.nan
    factor_df = pd.DataFrame(f_data['c2v'].unstack().rolling(5, min_periods=1).mean().stack())
    factor_df.columns = [factor_name]
    # ----------------------------------------close 2 vwap 的最近5日比值 44.83 -10.23 与skk_v2c_mean_a高相关---------------------------------------------------------------------------
    return factor_df