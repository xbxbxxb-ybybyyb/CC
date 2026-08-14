# coding: utf-8
# Author：fengchi863
# Date ：2023/7/4 20:52

import pandas as pd
from xquant.factordata import FactorData
s = FactorData()

def factor_fc_nextT1_5(start_date, end_date, IO, return_fillna_dic=False):
    import sys
    factor_name = sys._getframe().f_code.co_name[7:]

    if return_fillna_dic:
        return {factor_name: 0, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date_ = int(s.tradingday(str(start_date), -60)[0])  # 向前取的天数至少大于要用到的数据日期数+1天
    md_data = IO.read_data([start_date_, end_date], columns=['close', 'high', 'open', 'pre_close', 'low', 'pct_chg']
                           , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    md_data['code'] = md_data.reset_index()['Ticker'].values
    md_data['datelist'] = md_data.reset_index()['dt'].map(lambda x: x.to_pydatetime().strftime('%Y%m%d')).values
    md_data['h2l_3d'] = (md_data['high'] - md_data['low']) / md_data['pre_close'].unstack().rolling(3, min_periods=1).mean().stack()
    md_data.loc[(md_data['code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'h2l_3d'] = md_data.loc[(md_data['code'].str.startswith('3')) & (md_data['datelist'] >= '20200824'), 'h2l_3d'] / 2
    factor_df = pd.DataFrame()
    factor_df[factor_name] = md_data['h2l_3d'].unstack().shift(1).stack()
    # -------------------------------------------------------K线实体柱，用昨收放缩，取3日平均---9.13 -1.91 与saturn_Minc_minus_mdd高相关---------------------------------------------------------
    return factor_df