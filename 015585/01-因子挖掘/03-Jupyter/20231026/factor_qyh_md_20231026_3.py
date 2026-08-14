import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_20231026_3'
# dtj,zcz
# pct*turn的3日最小值
# -0.07,38
# skk_prs_rmin：32
def factor_qyh_md_20231026_3(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -4,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['pct_chg','turn','pre_close'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                df_ori.reset_index()['dt'] >= '2020-08-24'))
                 | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    df_ori.loc[df_ori['zcz'] == 1, 'pct_chg'] = df_ori.loc[df_ori['zcz'] == 1, 'pct_chg']/2
    df_ori[factor_name] = (df_ori['pct_chg'] * df_ori['turn']).unstack().rolling(3,1).min().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
