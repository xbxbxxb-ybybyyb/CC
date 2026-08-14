# -*- coding: utf-8 -*-
# @Time    : 2023/02/01 20:15
# @Author  : qinyuhao

# 逻辑：T-2日最大破板幅度
# 计算每日最高价之后的最低价，计算幅度
import pandas as pd
import numpy as np
import os
from xquant.factordata import FactorData
s = FactorData()
factor_name = 'qyh_2t_max_uldown'
def factor_qyh_2t_max_uldown(start_date, end_date, IO, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -1}
    # -------------------------------------------------------------------------------------------------------------------
    start_date = int(s.tradingday(str(start_date), -20)[0])
    # 计算当日是否涨停
    f_data = IO.read_data([start_date, end_date],
                          columns=['close','pre_close','high','low']
                          , alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
    f_data['p_zt'] = np.floor(f_data['pre_close']*100*1.1+0.5)/100
    f_data['p_dt'] = np.floor(f_data['pre_close']*100*0.9+0.5)/100
    f_data['is_ZT'] = f_data['high'] >= f_data['p_zt']
    # # 计算当日最高价所属时间
    # g_data = IO.read_data([start_date, end_date],
    #                        alt='/data/group/800463/data/generalStrong/minute5/high.h5')
    # columns_ = []
    # for i in g_data.columns:
    #     columns_.append(int(i[1:]))
    # g_data.columns = columns_
    # g_data['high'] = g_data.stack().groupby(['dt', 'Ticker']).max()
    # g_data['high_time'] = g_data.stack().groupby(['dt', 'Ticker']).apply(lambda x: x[x == x.max()].index[0][2])
    # # 计算最高价时间以后的最低价
    # h_data = IO.read_data([start_date, end_date],
    #                       alt='/data/group/800463/data/generalStrong/minute5/low.h5')
    # h_data.columns = columns_
    # h_data['high_time'] = g_data['high_time']
    # h_data_tmp = h_data.stack().reset_index().set_index(['dt', 'Ticker'])
    # def get_min(x):
    #     x_high_time = x[x['level_2'] == 'high_time'][0].values[0]
    #     #     print(x)
    #     x = x.iloc[:-1]
    #     res = x[x['level_2'] > x_high_time]
    #     return res.min()[0]
    # g_data['min'] = h_data_tmp.groupby(['dt', 'Ticker']).apply(
    #     lambda x: get_min(x))
    # g_data['is_zt'] = f_data['is_ZT'] # 记录当日是否涨停
    # g_data.to_pickle('/data/user/015585/01-因子挖掘/05-Saturn/20230621/每日破板.pkl')
    #
    g_data = pd.read_pickle('/data/user/015585/01-因子挖掘/05-Saturn/20230621/每日破板.pkl')
    g_data['change'] = (g_data['high'] - g_data['min'])/g_data['high']
    g_data.loc[(f_data[f_data['is_ZT'] == 0].index) & (g_data.index), 'change'] = np.nan
    g_data[factor_name] = (g_data['change'].unstack() - g_data['change'].unstack().shift(1)).stack()
    #
    res = pd.DataFrame(g_data[factor_name])

    # -------------------------------------------------------------------------------------------------------------------
    return res

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。