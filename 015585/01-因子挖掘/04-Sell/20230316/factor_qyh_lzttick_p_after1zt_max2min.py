# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：首次封板后砸开的最大幅度
# score: -0.065，12
# Lzt_tot_open_zt_time：-0.09
# lzt_label_pattern
factor_name = 'qyh_lzttick_p_after1zt_max2min'#
def factor_qyh_lzttick_p_after1zt_max2min(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 10000000}
    p_zt = tick_df['LastPx'].max()
    time = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()
    p_df = tick_df[tick_df['MDTime'] >= time]['LastPx']
    ratio = (p_df.max() - p_df.min()) / tick_df['pre_close'].mean()
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
