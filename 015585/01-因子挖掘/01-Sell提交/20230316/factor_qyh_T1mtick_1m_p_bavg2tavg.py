# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_T1mtick_1m_p_bavg2tavg'#
def factor_qyh_T1mtick_1m_p_bavg2tavg(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.03}

    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    col_list_p = ['Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price',
                  'Buy6Price', 'Buy7Price', 'Buy8Price', 'Buy9Price','Buy10Price',
                  'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price',
                  'Sell6Price', 'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price']
    pre = tick_df['pre_close'].mean()
    df_b12s1 = ((tick_df['amt'] / tick_df['vol']) - tick_df['WeightedAvgBidPx']) / pre
    delta = df_b12s1.mean()
    factor_dict = {factor_name: delta}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
