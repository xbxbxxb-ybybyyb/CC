# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 不提交，提交复合的
# 逻辑：首次到末次涨停的成交额
# score:-0.07,12    封板前，成交额越高越好（充分换手）
# Lzt_tot_open_zt_time:13,-0.09
# lzt_label_pattern:8,0.06
factor_name = 'qyh_lzttick_amt_after12zt'#
def factor_qyh_lzttick_amt_after12zt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 10000000}
    p_zt = tick_df['LastPx'].max()
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    # 末次涨停时间
    time = tick_df[(tick_df['LastPx'] == p_zt)&(tick_df['LastPx_1'] != p_zt)]['MDTime'].max()
    # 首次涨停时间
    time_1 = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()
    #
    amt_df = tick_df[(tick_df['MDTime'] >= time_1) & (tick_df['MDTime'] <= time)]['TotalValueTrade']
    amt = amt_df.max() - amt_df.min()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
