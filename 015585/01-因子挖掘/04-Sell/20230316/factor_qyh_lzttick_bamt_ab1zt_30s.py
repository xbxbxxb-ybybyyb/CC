# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：首次涨停前后的挂买金额之比
# score:7,0.059
# sss_lzo_bigofiap_max(0.72):16,0.09
factor_name = 'qyh_lzttick_bamt_ab1zt_30s'#
def factor_qyh_lzttick_bamt_ab1zt_30s(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    p_zt = tick_df['LastPx'].max()
    # 末次涨停时间
    time_1 = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()
    #
    tick_df_1 = tick_df[tick_df['MDTime'] > time_1]
    if len(tick_df_1) >= 10:
        amt_1 = (tick_df_1['TotalBidQty'] * tick_df_1['WeightedAvgBidPx']).head(10).sum()
    else:
        amt_1 = (tick_df_1['TotalBidQty'] * tick_df_1['WeightedAvgBidPx']).sum()
    #
    tick_df_2 = tick_df[tick_df['MDTime'] < time_1]
    if len(tick_df_2) >= 10:
        amt_2 = (tick_df_2['TotalBidQty'] * tick_df_2['WeightedAvgBidPx']).tail(10).sum()
    else:
        amt_2 = (tick_df_2['TotalBidQty'] * tick_df_2['WeightedAvgBidPx']).sum()
    factor_dict = {factor_name: amt_1/amt_2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
