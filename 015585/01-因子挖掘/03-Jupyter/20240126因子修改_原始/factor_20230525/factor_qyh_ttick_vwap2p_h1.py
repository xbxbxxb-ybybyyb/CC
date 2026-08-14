# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_vwap2p_h1'#
def factor_qyh_ttick_vwap2p_h1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.9957}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    if zcz:
        tick_df['vwap'] = (tick_df['vwap']/pre - 1)/2 + 1
        tick_df['LastPx'] = (tick_df['LastPx'] / pre - 1) / 2 + 1
    length = int(len(tick_df)/2)
    if length > 0:
        ratio = (tick_df['vwap']/tick_df['LastPx']).head(length).mean()
    else:
        ratio = np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
