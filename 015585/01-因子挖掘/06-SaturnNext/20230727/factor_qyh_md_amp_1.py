# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

# 逻辑：计算T-1振幅，对abs超过20%的部分截断
#
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'md_qyh_amp_1'
def factor_qyh_md_amp_1(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.06,'data':['MD']}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -40)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['high','low']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['low'] = f_data['low'].apply(lambda x: np.nan if abs(x) <= 0.0001 else x)#最近停牌或其他问题的，作为0处理
    f_data['amp'] = f_data['high'] / f_data['low'] - 1
    # 注册制截断(1.1/0.9 = 1.22)
    f_data['amp'] = f_data['amp'].apply(lambda x: 0.22 if x>0.22 else x)
    f_data['amp'] = f_data['amp'].apply(lambda x: -0.22 if x<-0.22 else x)
    # 1日均值
    f_data[factor_name] = f_data['amp']
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。