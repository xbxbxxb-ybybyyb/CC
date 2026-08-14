import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
# dtj
# amt在过去60日的变异系数
# 40,0.07
factor_name = 'qyh_next_md_20231130_10'
def factor_qyh_next_md_20231130_10(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -80)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','turn','amt','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             df_ori.reset_index()['dt'] >= '2020-08-24'))
    #              | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    #
    # df_ori['factor1'] = df_ori['turn']
    # df_ori['factor2'] = df_ori['turn'].unstack().rolling(60,1).median().stack()
    #
    df_ori[factor_name] = df_ori['amt'].unstack().rolling(60,5).mean().stack() / (df_ori['amt'].unstack().rolling(60,5).std().stack()+1)
    # df_ori[factor_name] = df_ori[factor_name].apply(lambda x : 10 if x > 10 else -10 if x < -10 else x)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
