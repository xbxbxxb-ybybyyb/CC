# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：量价相关性（不包括集合竞价),对价格做分组聚合处理
# 0
factor_name = 'qyh_T1mtra_corr_pa_1_ma'#price and amt
def factor_qyh_T1mtra_corr_pa_1_ma(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0]  # 只看成交的
    transaction_df = transaction_df[transaction_df['TradeBSFlag'] != 0]# 0931
    pa = transaction_df.groupby('TradePrice').sum()['TradeMoney'].reset_index().sort_values('TradePrice')
    # 分组平均
    length = len(pa)
    segment = min(int(length/5), 10)
    if segment >= 5:
        num_each = int(length / segment)
        group_index_list = []
        for i in range(segment):
            group_index_list = (group_index_list + [i] * num_each) if i != (segment - 1) \
                else (group_index_list + [i] * (length - num_each * segment + num_each))
        pa['group'] = group_index_list
        pa_corr = pa.groupby('group').sum()['TradeMoney'].corr(pa.groupby('group').mean()['TradePrice'])
    else:
        pa_corr = np.nan
    factor_dict = {factor_name: abs(pa_corr)}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
