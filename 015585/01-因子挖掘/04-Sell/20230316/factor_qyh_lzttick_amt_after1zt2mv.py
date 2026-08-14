# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：首次涨停后的成交额 / 流动市值
# score:-0.06,7.5:标准化之后的效果更强一些
# free_turn
factor_name = 'qyh_lzttick_amt_after1zt2mv'#
def factor_qyh_lzttick_amt_after1zt2mv(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 5*60*1000}
    p_zt = tick_df['LastPx'].max()
    # tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    time = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()# 首次封板时间
    amt_df = tick_df[tick_df['MDTime'] >= time]['TotalValueTrade']
    amt = amt_df.max() - amt_df.min()
    mv = tick_df['pre_close'].mean() * tick_df['ff_shares'].mean()
    factor_dict = {factor_name: amt*1000/mv}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
