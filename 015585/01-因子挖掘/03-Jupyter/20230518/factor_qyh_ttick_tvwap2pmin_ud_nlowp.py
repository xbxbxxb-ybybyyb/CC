# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 不提交
# 逻辑：去除极端价格后，上涨和下跌的vwap除以最新价的最小值时间

factor_name = 'qyh_ttick_tvwap2pmin_ud_nlowp'#
def factor_qyh_ttick_tvwap2pmin_ud_nlowp(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 30}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['tradep'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    tick_df2 = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    p_low = tick_df['LastPx'].quantile(0.25)
    tick_df1 = tick_df1[tick_df1['LastPx'] >= p_low]
    tick_df2 = tick_df2[tick_df2['LastPx'] >= p_low]

    tick_df1['vwap'] = tick_df1['TotalValueTrade'].cumsum()/tick_df1['TotalVolumeTrade'].cumsum()
    tick_df1 = tick_df1[(tick_df1['vwap']/tick_df1['LastPx']) == (tick_df1['vwap']/tick_df1['LastPx']).min()].head(1)
    t1 = tick_df1['MDTime'].mean()
    tick_df2['vwap'] = tick_df2['TotalValueTrade'].cumsum()/tick_df2['TotalVolumeTrade'].cumsum()
    tick_df2 = tick_df2[(tick_df2['vwap']/tick_df2['LastPx']) == (tick_df2['vwap']/tick_df2['LastPx']).min()].head(1)
    t2 = tick_df2['MDTime'].mean()
    factor_dict = {factor_name: t1-t2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
