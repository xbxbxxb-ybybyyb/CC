# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
from xquant.factordata import FactorData
#
# 逻辑：突破小平台
'''
1、取过去30日至当日的极差，保留小于25%的最远日期
2、取这段时间的最高价（不包括当日），与当前价格比较，当前价格在最高价*0.9以上才有效，越高越好，但不能=他本身
3、最远日期向前20日的涨跌幅需要>20%，最远日期到当日需要>5天，最远日期到当日的平均成交量>50日平均成交量
 = 最远日期到当日间隔 * 0.1 + 当前价格/最高价 + 最远日期以后vol/50日vol
'''
#
s = FactorData()
factor_name = 'qyh_up_pf'#
def factor_qyh_up_pf(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # 可修改的因子编写部分
    # 该部分与alpha因子计算方式一致，计算全部股票在全部时间区间上的因子值，之后会在run_factor_demo函数中进行向后平移一天和样本的筛选
    # 返回dt, Ticker格式multiindex的DataFrame, 一列，列名为因子名称
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -100)[0])
    f_data = IO.read_data([start_date, end_date],
                          columns=['close', 'high', 'low', 'amt'],
                          alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['amt'] = f_data['amt'].apply(lambda x:np.nan if x == 0 else x)
    f_data['amt'] = f_data['amt'].unstack().fillna(method='ffill',limit=30).stack()
    f_data['close'] = f_data['close'].apply(lambda x:np.nan if x == 0 else x)
    f_data['close'] = f_data['close'].unstack().fillna(method='ffill',limit=30).stack()
    f_data['pct20'] = (f_data['close'].unstack()/f_data['close'].unstack().shift(20) - 1).stack()
    list_col = []
    f_data_high_un = f_data['high'].unstack()
    f_data_low_un = f_data['low'].unstack()
    f_data_amt_un = f_data['amt'].unstack()
    f_data_pct20_un = f_data['pct20'].unstack()
    for i in range(5, 30):
        print(i)
        f_data['range_' + str(i)] = (f_data_high_un.rolling(i, i - 4).max().stack()) / \
                                    (f_data_low_un.rolling(i, i - 4).min().stack()) - 1
        f_data['max_' + str(i)] = f_data_high_un.rolling(i, i - 4).max().stack()  # i日以内的最高价
        f_data['amt_' + str(i)] = f_data_amt_un.rolling(i, i - 4).mean().stack()
        f_data['pct20_' + str(i)] = f_data_pct20_un.shift(i).stack()
        list_col.append(i)
    def get_max_date(x):
        for i in list_col:
            if x['range_' + str(i)] > (0.1 + i / 500):
                return i
        return i
    f_data['max_date'] = f_data.apply(lambda x: get_max_date(x), axis=1)  # 最大日期
    f_data['max'] = f_data.apply(lambda x: x['max_' + str(int(x['max_date']))], axis=1)  # 最大日期以内的最高价
    print('get max')
    f_data['amt_50'] = f_data_amt_un.rolling(50, 40).mean().stack()
    f_data['amt_amax'] = f_data.apply(lambda x: x['amt_' + str(int(x['max_date']))], axis=1)
    print('get amt_amax')
    f_data['score2'] = f_data['close'] / f_data['max']
    f_data['score2'] = f_data['score2'].apply(lambda x: -2 if abs(x - 1) <= 0.01 else x)
    f_data['score3'] = f_data['amt_amax'] / f_data['amt_50']
    f_data['score3'] = f_data['score3'].apply(lambda x : 1.5 if x > 1.5 else x)
    f_data['pct20_max'] = f_data.apply(lambda x: x['pct20_' + str(int(x['max_date']))],axis = 1)
    print('get pct20_max')
    f_data[factor_name] = f_data.apply(lambda x :
                                       (x['max_date'] * 0.02 + x['score2'] + x['score3']) if x['pct20_max']>0.2
                                       else -(x['max_date'] * 0.02 + x['score2'] + x['score3']),axis = 1)
    f_data.to_pickle('/data/user/015585/01-因子挖掘/03-Jupyter/20230427/f_data.pkl')
    f_data = pd.DataFrame(f_data[factor_name])
    # -------------------------------------------------------------------------------------------------------------------
    return f_data

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
