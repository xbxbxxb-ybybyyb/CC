# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

# gg
# 计算10日收盘价MA,factor = close/ma
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_md_ma_10'
def factor_qyh_md_ma_10(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.56,'data':['MD']}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -40)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close','amt','volume','open']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['vwap'] = f_data['amt'] / f_data['volume']
    f_data['ma_10'] = f_data['vwap'].unstack().rolling(5,1).mean().stack()
    # f_data['zcz'] = (((f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
    #             f_data.reset_index()['dt'] >= '2020-08-24'))
    #              | (f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    f_data[factor_name] = f_data['close'] / f_data['ma_10'] - 1
    f_data[factor_name] = f_data[factor_name].unstack().rank(axis=1).stack()
    f_data[factor_name] = f_data[factor_name] / f_data[factor_name].unstack().max(axis=1)
    # f_data.loc[f_data['zcz'] == 1,factor_name] = f_data.loc[f_data['zcz'] == 1,factor_name] / 2
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data