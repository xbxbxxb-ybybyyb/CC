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

def factor_fc_nextT1_20231221_36(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    def process(md_data):
        md_data.loc[md_data['pct_chg'] > 10, 'pct_chg'] = 10  # 截断
        md_data.loc[md_data['pct_chg'] < -10, 'pct_chg'] = -10  # 截断

        md_data['open'] = md_data['open'] * md_data['adjfactor']
        md_data['close'] = md_data['close'] * md_data['adjfactor']
        md_data['high'] = md_data['high'] * md_data['adjfactor']
        md_data['low'] = md_data['low'] * md_data['adjfactor']
        md_data['vwap'] = md_data['vwap'] * md_data['adjfactor']
        md_data['pre_close'] = md_data['pre_close'] * md_data['adjfactor']
        return md_data

    def sub_mean(x):
        x = x - x.mean()
        return x

    if return_fillna_dic:
        return {factor_name: 0, 'data': ['MD']}
        # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -360)[0])
    md_data = IO.read_data([start_date_, end_date], alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    process(md_data)

    md_data['pct_chg'] = md_data['pct_chg'].groupby(level=[0]).apply(lambda x: sub_mean(x))
    md_data['turn'] = md_data['turn'].groupby(level=[0]).apply(lambda x: sub_mean(x))
    md_data['res'] = md_data['pct_chg'] * md_data['turn']
    res_std = md_data['res'].unstack().rolling(120, min_periods=5).std().stack()

    factor_df = pd.DataFrame()
    factor_df[factor_name] = (md_data['res'] - res_std).unstack().rolling(240, min_periods=1).median().stack()
    # ---------------------------------------------------------------------------------------------------------------------
    """
    对pct和成交量进行放缩，计算其乘积的近1年的中位值
    13.5 -0.0357
    =====>>>> 13.5 -0.035763971088629984 -24.103005744592753 36.719397405819265 float_shares，Next_float_shares 0.6154，0.6151
    """
    return factor_df