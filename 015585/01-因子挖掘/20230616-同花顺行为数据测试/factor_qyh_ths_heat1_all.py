# -*- coding: utf-8 -*-
# @Time    : 2023/02/01 10:15
# @Author  : qinyuhao

import pandas as pd
import os
from xquant.factordata import FactorData
import numpy as np
import csv
s = FactorData()
def factor_qyh_ths_heat1_all(start_date, end_date, IO, return_fillna_dic=False):
    factor_name = 'factor_qyh_ths_heat1_all'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    df = pd.read_csv('同花顺人气--2019.csv')
    df['code'] = df['证券代码'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['date'] = df['日期'].apply(lambda x: pd.Timestamp(x))
    df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df = df[['date','code','当日关注粘性']]
    print(df.columns)
    df.columns = ['dt','Ticker',factor_name]
    # df = df.drop(['日期','证券代码','证券简称'],axis =1)
    df = df.set_index(['dt', 'Ticker'])
    # df[factor_name] = df[factor_name] / (df[factor_name].unstack().shift(1).stack()+0.1) - 1
    df[factor_name] = df[factor_name].unstack().rolling(5,1).mean().stack()
    # df[factor_name] = df[factor_name].unstack().rolling(7, 1).std().stack()
    df_test = pd.DataFrame(df[factor_name]).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    # -------------------------------------------------------------------------------------------------------------------
    return df_test