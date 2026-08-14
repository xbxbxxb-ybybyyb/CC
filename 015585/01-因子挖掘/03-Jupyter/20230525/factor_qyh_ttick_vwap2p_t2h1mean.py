# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：触发前vwap/最新价 - 前一半vwap/最新价均值
# 快速：0.132，77
# 全样本：0.15，76
#
factor_name = 'qyh_ttick_vwap2p_t2h1mean'#
def factor_qyh_ttick_vwap2p_t2h1mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.04}
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    tick_df = tick_df[tick_df['LastPx'] > 0]
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    ratio1 = (tick_df['vwap']/tick_df['LastPx']).tail(1).mean()
    length = int(len(tick_df)/2)
    if length > 0:
        ratio2 = (tick_df['vwap']/tick_df['LastPx']).head(length).mean()
    else:
        ratio2 = np.nan
    ratio = ratio1 - ratio2
    if len(tick_df) < 20:
        ratio = ratio - (len(tick_df)/20)*0.02
    if len(tick_df) > 60:
        tick_df = tick_df.tail(60)
        lim = (tick_df['LastPx'].max() - tick_df['LastPx'].min())/tick_df['pre_close'].max() - 1
        if lim > 0.06:
            ratio = ratio - lim/0.06*0.03
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
