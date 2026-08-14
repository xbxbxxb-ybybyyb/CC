# -*- coding: utf-8 -*-
# @Time    : 2023/02/01 10:15
# @Author  : qinyuhao

import pandas as pd
import os
from xquant.factordata import FactorData
import numpy as np
import csv
s = FactorData()
def factor_qyh_ths_index1(start_date, end_date, IO, return_fillna_dic=False):
    factor_name = 'factor_qyh_ths_index1'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: np.nan}
    df = pd.read_csv('thsindex1.csv')
    df['code'] = df['code'].apply(lambda x: str(x).zfill(6))  # 补tradingcode的0
    df['date'] = df['date'].apply(lambda x: pd.Timestamp(x))
    df['code'] = df['code'].apply(lambda x: x + '.SH' if x.startswith('6') else x + '.SZ')
    df.columns = ['dt', 'Ticker', 'name', 'ori']
    df = df.set_index(['dt', 'Ticker'])
    df['change'] = (df['ori'].unstack() / df['ori'].unstack().shift(1) - 1).stack()
    df = df['change'].unstack()
    def get_lma(a,n):
        weight = [(n-i)/(n+1)/n*2 for i in range (0,n)]
        counter = 1
        df = pd.DataFrame()
        for x in weight:
            if (counter == 1):
                df = a*x
            else:
                df = df + a.shift(counter-1)*x
            counter += 1
        return df
    df = pd.DataFrame(get_lma(df,20).stack())
    df.columns = [factor_name]
    df_test = pd.DataFrame(df[factor_name]).loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
    # -------------------------------------------------------------------------------------------------------------------
    return df_test