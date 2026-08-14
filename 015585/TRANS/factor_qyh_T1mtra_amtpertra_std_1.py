# -*- coding: utf-8 -*-
# @Time    : 2023/02/08 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：T日09:31数据，标准化单笔成交额:除以T-1自由流通市值
# score:-0.047,1
factor_name = 'qyh_T1mtra_amtpertra_std_1'
def factor_qyh_T1mtra_amtpertra_std_1(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.111}
    transaction_df = transaction_df[(transaction_df['TradePrice'] > 0)]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000]
    if transaction_df.empty:
        amtpertra = 0
    else:
        amtpertra = transaction_df['TradeMoney'].sum() / transaction_df['TradeMoney'].count()
    # 自由流通市值
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    # 标准化
    if mv == 0:
        amtpertra_std = np.nan
    else:
        amtpertra_std = amtpertra / mv
    factor_dict = {factor_name: amtpertra_std}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
