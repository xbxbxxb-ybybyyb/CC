# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：(首次到末次涨停的成交额 - 末次涨停以后的成交额) / 30s成交额的最大值,如果首末相同，取涨幅>9%
# score:19，-0.1
# lzt_label_pattern
# lzt_day_pattern
# jpt_label_pattern
factor_name = 'qyh_lzttick_amt_after2to12zt_2max30s_1'#
def factor_qyh_lzttick_amt_after2to12zt_2max30s_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.54}
    p_zt = tick_df['LastPx'].max()
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    tick_df['amt'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1)
    # tick_df['amt'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1)
    # 末次涨停时间
    time = tick_df[(tick_df['LastPx'] == p_zt)&(tick_df['LastPx_1'] != p_zt)]['MDTime'].max()
    # 首次涨停时间
    time_1 = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()
    # 首末之间
    amt_df = tick_df[(tick_df['MDTime'] >= time_1) & (tick_df['MDTime'] <= time)]['TotalValueTrade']
    amt = amt_df.max() - amt_df.min()
    if amt < 10:
        tick_df_1 = tick_df[tick_df['MDTime'] <= time_1]
        amt = tick_df_1[tick_df_1['LastPx'] >= (1.09 * tick_df_1['pre_close'].mean())]['amt'].sum()
    # 末次以后
    amt_df_2 = tick_df[tick_df['MDTime'] > time]['TotalValueTrade']
    amt_2 = amt_df_2.max() - amt_df_2.min()
    #　max30S
    amt_max30s = tick_df['amt'].rolling(10,1).sum().max()
    ratio = (amt - amt_2)/amt_max30s
    if ratio >= 5:
        ratio = 5
    if ratio <= -3:
        ratio = -3
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
