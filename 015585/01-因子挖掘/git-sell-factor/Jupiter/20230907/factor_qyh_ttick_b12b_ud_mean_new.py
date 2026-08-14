# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_b12b_ud_mean_new'#
def factor_qyh_ttick_b12b_ud_mean_new(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 3.2}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
    tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    #
    if tick_df1.empty:
        pct1 = np.nan
    else:
        pct1 = ((tick_df1['Buy5Price'] - tick_df1['WeightedAvgBidPx']) / pre_close).mean()
    if tick_df2.empty:
        pct2 = np.nan
    else:
        pct2 = ((tick_df2['Buy5Price'] - tick_df2['WeightedAvgBidPx']) / pre_close).mean()
    #
    pct = pct1 - pct2
    if zcz:
        pct = pct/2
    factor_dict = {factor_name: pct*1000}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
