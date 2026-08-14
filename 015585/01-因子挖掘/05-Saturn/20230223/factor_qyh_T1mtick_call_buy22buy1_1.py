# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：集合竞价24到25，买2的和/买1的和
# score:0
#
factor_name = 'qyh_T1mtick_call_buy22buy1_1'#
def factor_qyh_T1mtick_call_buy22buy1_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 92400000]
    tick_df = tick_df[tick_df['TradingPhaseCode'] == '1'] # 0924以后的集合竞价
    qty_buy2 = tick_df['Buy2OrderQty'].sum()
    qty_total = tick_df['Buy1OrderQty'].sum()
    if qty_total > 10:
        ratio = qty_buy2/qty_total
    else:
        ratio = 0
    factor_dict = {factor_name: ratio}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
