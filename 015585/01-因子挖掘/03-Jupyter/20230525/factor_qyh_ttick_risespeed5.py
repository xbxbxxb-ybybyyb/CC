# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：拉升速度：分钟涨跌幅超过0.5%的时间占比
# 快速:0.06,20
# 全样本：
#
factor_name = 'qyh_ttick_risespeed5'#
def factor_qyh_ttick_risespeed5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.1}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['speed'] = (tick_df['LastPx'] - tick_df['LastPx'].shift(20))/tick_df['pre_close'].max()
    if tick_df.empty:
        rs = 0.25
    else:
        rs = len(tick_df[tick_df['speed'] >= 0.005]) / len(tick_df)
    factor_dict = {factor_name: rs}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
