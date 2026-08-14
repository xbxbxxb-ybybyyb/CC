# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 10:15
# @Author  : qinyuhao

# 已提交：0216
# 逻辑：理想反转因子2.0：根据5min基础数据，计算过去20日中每一日的“5min最高单笔成交金额”（记为x），取x最大(最小）的10个交易日，对其涨跌幅求和，再将两部分作差
# 逻辑：该逻辑与研报原始逻辑有差别，研报原始逻辑是取单笔成交金额的高分位数作为x
# score:22，-0.07
# 无corr
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_return_ideal_20_q'
def factor_qyh_return_ideal_20_q(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.6975}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -60)[0])
    # 买单委托笔数，这里用买单委托笔数代替成交笔数
    g1_data = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/ordersheet5/TotalBidQty.h5')
    g1_data.replace(0,np.nan,inplace = True)
    # 成交额
    g2_data = IO.read_data([start_date, end_date],
                           alt='/data/group/800463/data/generalStrong/minute5/amt.h5')
    # 5min最高平均单笔金额
    g_data =  (g2_data / g1_data).max(axis = 1)
    del g1_data,g2_data
    # 涨跌幅做截断处理
    f_data = IO.read_data([start_date, end_date],
                          columns=['pct_chg'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['pct_chg'] = f_data['pct_chg'].apply(lambda x: 10 if x >=10 else -10 if x <= -10 else x)
    # 把20日内涨跌幅，按照5min最高平均单笔金额排序，排序靠前的日期的涨跌幅为正，否则添加负号
    dt_list = list(set(g_data.index.get_level_values(0)))
    dt_list.sort()
    res = pd.DataFrame()
    sita = 0.5
    for dt in dt_list:
        # print(dt)
        if dt >= dt_list[19]:
            dt_s = dt_list[dt_list.index(dt) - 19]
            df_dt = g_data.loc[dt_s:dt].unstack().rank(axis=0)
            df_dt = (df_dt / df_dt.max(axis=0)).stack()
            df_dt = df_dt.apply(lambda x: 1 if x > (1 - sita) else -1 if x < sita else 0)
            res_dt = (df_dt.unstack() * f_data['pct_chg'].loc[dt_s:dt].unstack()).mean(axis=0)
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