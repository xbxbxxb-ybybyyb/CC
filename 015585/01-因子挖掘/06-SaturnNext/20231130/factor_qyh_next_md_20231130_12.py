import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_next_md_20231130_12'
# dtj
# T-1日的pct*turn的绝对值，除以60日中位数，相对于60日均值的超额
# 29，-0.062
def factor_qyh_next_md_20231130_12(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    def rank_(data_):
        data_r = (data_.unstack().rank(axis=1) / (~ data_.unstack().isnull()).values.sum(axis=1).reshape(-1, 1)).stack()
        return data_r
    start_date = int(s.tradingday(str(start_date), -150)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','pre_close','turn','pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    # df_ori['zcz'] = (((df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             df_ori.reset_index()['dt'] >= '2020-08-24'))
    #              | (df_ori.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    #
    df_ori['factor'] = abs(df_ori['pct_chg']) * df_ori['turn']
    #
    df_ori[factor_name] = df_ori['factor'] / df_ori['factor'].unstack().rolling(60,1).median().stack()
    df_ori[factor_name] = df_ori[factor_name].apply(lambda x : 200 if x > 200 else 0 if x < 0 else x)
    df_ori[factor_name] = df_ori[factor_name] - df_ori[factor_name].unstack().rolling(60,1).mean().stack()
    # df_ori[factor_name] = rank_(df_ori[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
