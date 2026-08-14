# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_talltick_v2p_p25_mean(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_v2p_p25_mean'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.999}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    p25 = tick_df['LastPx'].quantile(0.25)
    tick_df = tick_df[tick_df['LastPx'] <= p25]
    tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    v2p = (tick_df['vwap']/tick_df['LastPx']).mean()
    factor_dict = {factor_name: v2p}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

