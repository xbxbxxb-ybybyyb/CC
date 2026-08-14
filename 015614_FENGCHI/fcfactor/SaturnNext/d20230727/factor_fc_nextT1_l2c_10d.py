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

def factor_fc_nextT1_l2c_10d(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -8)[0])
    md_data = IO.read_data([start_date_, end_date], columns=['amt', 'high', 'low', 'turn', 'pct_chg', 'pre_close'],
                           alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')

    md_data['pct'] = (md_data['low'] - md_data['pre_close']) / md_data['pre_close']
    md_data['factor'] = (md_data['pct'] - md_data['pct_chg']) * np.log(md_data['turn'])

    factor_df = pd.DataFrame(md_data['factor'].unstack().rolling(10, min_periods=1).sum().stack())
    factor_df.columns = [factor_name]
    # ----------------------------------最低价与收盘价只差相对于昨收，10日平均 28.041666666666664 0.06620206480281762-subumit------------------------------------------------------------------------------
    return factor_df