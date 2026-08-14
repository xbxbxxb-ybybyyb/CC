# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：(首次到末次涨停的成交额 - 末次涨停以后的成交额) / (首次到末次涨停的成交额 + 末次涨停以后的成交额)
# score:-0.08,13
# sss_lztk_ztbuypstat_cv_zt:-0.11,19
factor_name = 'qyh_lzttick_amt_after2to12zt_2max30s_2'#
def factor_qyh_lzttick_amt_after2to12zt_2max30s_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.38}
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
    # 末次以后
    amt_df_2 = tick_df[tick_df['MDTime'] > time]['TotalValueTrade']
    amt_2 = amt_df_2.max() - amt_df_2.min()

    ratio = (amt - amt_2)/(amt + amt_2)
    if ratio >= 0.8:
        ratio = 0.8
    if ratio <= -0.5:
        ratio = -0.5
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
