# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_m5_price_v_sm'
def factor_qyh_m5_price_v_sm(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2,'data':['minute5']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    g1_data = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/minute5/close.h5')
    g1_data.replace(0, np.nan, inplace=True)
    g1_data_1 = g1_data.T.shift(1).T
    g1_data_pct = (((g1_data / g1_data_1) - 1) * 100)  # pct_chg
    print('get_g1_data')
    g2_data = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/minute5/volume.h5')  # 成交量
    s_data = abs(g1_data_pct) * 1000 / (np.log(g2_data))  # smart，越大越聪明
    g3_data = g2_data.sum(axis=1).unstack().rolling(10).sum() * 0.2  # 过去10日成交量的20%
    print('get_g3_data')

    dt_list = list(set(g1_data.index.get_level_values(0)))
    dt_list.sort()
    g2_data_swap = g2_data.swaplevel()
    g1_data_swap = g1_data.swaplevel()
    del g1_data,g2_data,g1_data_1,g1_data_pct

    df_res = pd.DataFrame()
    for ticker, ticker_data in s_data.groupby('Ticker'):
        print(ticker)
        g1_data_swap_ticker = g1_data_swap.loc[ticker]
        g2_data_swap_ticker = g2_data_swap.loc[ticker]
        for dt in ticker_data.index.get_level_values(0):
            if dt >= dt_list[9]:
                dt_s = dt_list[dt_list.index(dt) - 9]
                array_s = np.array(ticker_data.loc[dt_s:dt]).flatten()  # 过去20天的s
                array_c = np.array(g1_data_swap_ticker.loc[dt_s:dt]).flatten()  # 过去20天的close
                array_v = np.array(g2_data_swap_ticker.loc[dt_s:dt]).flatten()  # 过去20天的volume
                index = np.argsort(-array_s)  # 从大到小
                array_c = np.nan_to_num(array_c[index])# 替换np.nan为0
                array_v = np.nan_to_num(array_v[index])
                index_20 = np.cumsum(array_v) <= g3_data.loc[dt, ticker] # 成交量累计值在前20%的索引
                res_sm = (array_v[index_20] * array_c[index_20]).sum() / (array_v[index_20].sum())
                res_all = (array_v * array_c).sum() / (array_v.sum())
                df_res.loc[dt,ticker] = res_sm / res_all
    df_res = (df_res - 1) * 100
    df_res = df_res.stack().reset_index()
    df_res.columns = ['dt', 'Ticker', factor_name]
    df_res = df_res.set_index(['dt', 'Ticker'])
    df_res = pd.DataFrame(df_res[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return df_res

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。