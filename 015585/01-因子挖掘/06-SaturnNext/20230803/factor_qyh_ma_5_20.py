# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

# 逻辑：根据5日、20日收盘价MA,计算MA5相对于MA20的偏离度，factor = (ma5 - ma20)/ma20
# SCORE:26
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_ma_5_20'
def factor_qyh_ma_5_20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -50)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['ma_5'] = f_data['close'].unstack().rolling(5,1).mean().stack()
    f_data['ma_5'] = f_data['ma_5'].apply(lambda x: 0 if abs(x) <= 0.0001 else x)#最近停牌或其他问题的，作为0处理
    f_data['ma_5'].replace(0, np.nan, inplace=True)
    f_data['ma_5'] = f_data['ma_5'].unstack().fillna(method='ffill',limit=20).stack()

    f_data['ma_20'] = f_data['close'].unstack().rolling(20,1).mean().stack()
    f_data['ma_20'] = f_data['ma_20'].apply(lambda x: 0 if abs(x) <= 0.0001 else x)#最近停牌或其他问题的，作为0处理
    f_data['ma_20'].replace(0, np.nan, inplace=True)
    f_data['ma_20'] = f_data['ma_20'].unstack().fillna(method='ffill',limit=20).stack()

    f_data[factor_name] = (f_data['ma_5'] - f_data['ma_20']) / f_data['ma_20']
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。