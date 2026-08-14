# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

# 逻辑：理想振幅因子：计算20日里每日振幅的均值，对abs超过20%的部分截断；对20日里close排序前20%的日振幅求和，后20%的日振幅求和，再将两者相减
# score:
# 高价部分(sita = 0.2)0.03, score = 13，说明高价部分的振幅仍然更具有反转特性
# 低价部分(sita = 0.2)0.07，score = 38，说明振幅的CORR主要来自于低价部分
# 低价部分(sita = 0.5)0.07，score = 52,但有2高CORR其他因子
# 高价部分(sita = 0.5)0.06, score = 44
# 最终尝试(sita = 0.2，只取低价部分，占比0.8)0.08,score = 57
# score(amp_20)=60 GG
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_amp_ideal_20_20'
def factor_qyh_amp_ideal_20_20(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -40)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['high','low','close']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['low'] = f_data['low'].apply(lambda x: 0 if abs(x) <= 0.0001 else x) #最近停牌或其他问题的，作为0处理
    f_data['low'].replace(0, np.nan, inplace=True)
    f_data['amp'] = f_data['high'] / f_data['low'] - 1
    # 注册制截断(1.1/0.9 = 1.22)
    f_data['amp'] = f_data['amp'].apply(lambda x: 0.22 if x>0.22 else x)
    f_data['amp'] = f_data['amp'].apply(lambda x: -0.22 if x<-0.22 else x)
    # 20日收盘价排序
    dt_list = list(set(f_data.index.get_level_values(0)))
    dt_list.sort()
    res = pd.DataFrame()
    sita = 0.2
    for dt in dt_list:
        print(dt)
        if dt >= dt_list[19]:
            dt_s = dt_list[dt_list.index(dt) - 19]
            df_dt = f_data['close'].loc[dt_s:dt].unstack().rank(axis=0)
            df_dt = (df_dt / df_dt.max(axis=0)).stack()
            df_dt = df_dt.apply(lambda x: 1 if x <= 1-sita else 0)
            res_dt = (df_dt.unstack() * f_data['amp'].loc[dt_s:dt].unstack()).mean(axis=0)
            res[dt] = res_dt
    res = pd.DataFrame(res.T.stack())
    res.columns = [factor_name]
    # -------------------------------------------------------------------------------------------------------------------
    return res

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。