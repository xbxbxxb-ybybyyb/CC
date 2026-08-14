# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：拉升速度：开盘后前一半 - 触发前3分钟涨跌幅超过0.5%的时间占比
# 快速:0.1,57（等权）0.1，65（归一化）0.11，73（前一半）
# 全样本：0.128,79（等权）,0.123,75(归一化)81，0.13（前一半）
#
factor_name = 'qyh_ttick_risespeed_c'#
def factor_qyh_ttick_risespeed_c(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.4}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['speed'] = (tick_df['LastPx'] - tick_df['LastPx'].shift(20))/tick_df['pre_close'].max()
    if len(tick_df) <= 61:
        rs = -0.5
    else:
        tick_df1 = tick_df.head(int(len(tick_df) / 2))
        rs1 = len(tick_df1[tick_df1['speed'] >= 0.005]) / len(tick_df1)
        tick_df2 = tick_df.tail(60)
        rs2 = len(tick_df2[tick_df2['speed'] >= 0.005]) / len(tick_df2)
        rs = rs1/0.12-rs2/0.24
    factor_dict = {factor_name: rs}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
