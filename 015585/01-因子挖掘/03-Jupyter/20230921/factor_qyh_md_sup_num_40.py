import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_sup_num_40'
#
# 过去40日上穿中轴线次数
# gg
def factor_qyh_md_sup_num_40(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2,'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -5)[0])
    df_ori = IO.read_data([start_date, end_date],
                          columns=['close','adjfactor'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    df_ori['close'] = df_ori['close'] * df_ori['adjfactor']
    df_ori['max'] = df_ori['close'].unstack().rolling(40,10).max().stack()
    df_ori['min'] = df_ori['close'].unstack().rolling(40,10).min().stack()
    df_ori['mid'] = (df_ori['max'] + df_ori['min']) / 2
    for i in range(1,41):
        df_ori['pre_'+str(i)] = df_ori['close'].unstack().shift(i).stack()
    list_up = []
    for i in range(2,41):
        df_ori['is_up_'+str(i)] = (df_ori['pre_' + str(i)] > df_ori['mid']) & \
                                  (df_ori['pre_' + str(i-1)] < df_ori['mid'])
        list_up.append('is_up_'+str(i))
    df_ori[factor_name] = df_ori[list_up].sum(axis=1)
    # -------------------------------------------------------------------------------------------------------------------
    return df_ori[[factor_name]]
