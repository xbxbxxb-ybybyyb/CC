# -*- coding: utf-8 -*-
# @Time    : 2023/02/01 10:15
# @Author  : qinyuhao

import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
def factor_qyh_md_plus_price_20_mean(start_date, end_date, IO, return_fillna_dic=False):
    factor_name='qyh_md_plus_price_20_mean'

    if return_fillna_dic:
        # 返回因子为nan时的填充值，Todo: T-1_factor类因子需要包括数据源缩写（其列表在因子规范数据源检测一节）
        return {factor_name: 0.0013, 'data':['MD']}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -30)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close','high','low']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['zcz'] = (((f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '30')) & (
                f_data.reset_index()['dt'] >= '2020-08-24'))
                 | (f_data.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
    f_data[factor_name] = 2 * f_data['close'] - f_data['high'] - f_data['low']
    f_data[factor_name] = f_data[factor_name].unstack().fillna(method='ffill',limit=10).stack()
    f_data['close_-1'] = f_data['close'].unstack().fillna(method='ffill',limit=10).shift(1).stack()
    f_data[factor_name] = f_data[factor_name] / f_data['close_-1']
    f_data.loc[f_data['zcz'] == 1,factor_name] = f_data.loc[f_data['zcz'] == 1,factor_name]/2
    print(f_data['zcz'].head(5))
    f_data = pd.DataFrame(f_data[factor_name])
    f_data = f_data.unstack().rolling(20,1).mean().stack()
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。