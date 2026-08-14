# -*- coding: utf-8 -*-
# @Time    : 2023/02/01 10:15
# @Author  : qinyuhao

import pandas as pd
import os
from xquant.factordata import FactorData
import numpy as np
import csv
s = FactorData()
def factor_qyh_ths_index4(start_date, end_date, IO, return_fillna_dic=False):
    factor_name = 'factor_qyh_ths_index4'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    df = pd.read_csv('thsindex4.csv')
    df['code'] = df['code'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
    df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df.columns = ['dt', 'Ticker', 'name', factor_name]
    #
    df = df.set_index(['dt'])
    df['mean'] = df.groupby('dt')[factor_name].count()
    df = df.reset_index().set_index(['dt','Ticker'])
    df[factor_name] = df[factor_name] * df['mean']
    df_test = pd.DataFrame(df[factor_name]).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    # -------------------------------------------------------------------------------------------------------------------
    return df_test