# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：末次封板后，每个tick挂买总额的最大值 / tttl
# score:28,0.14
# Lzt_pj2r_sell_buy_number_corr
factor_name = 'qyh_lzttick_bamt_after2zt_max_2tttl'#
def factor_qyh_lzttick_bamt_after2zt_max_2tttl(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 80000000}
    tick_df['amt'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1)
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    # amt ttl
    amt_ttl = tick_df['TotalValueTrade'].max()
    #
    p_zt = tick_df['LastPx'].max()
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    # 末次涨停时间
    time_1 = tick_df[(tick_df['LastPx'] == p_zt)&(tick_df['LastPx_1'] != p_zt)]['MDTime'].max()
    tick_df = tick_df[tick_df['MDTime'] >= time_1]
    #
    tick_df['buytotal'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    amt = tick_df['buytotal'].max()
    factor_dict = {factor_name: amt / amt_ttl}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
