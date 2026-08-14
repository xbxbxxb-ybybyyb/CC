# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：930以后，买卖单号的corr
# score:0.085,49,del num后为0.081，45  spearman:调整后为0.084，34
# max_rise_pct:-0.11,51
factor_name = 'qyh_TTra_corr_bsno_a930'
def factor_qyh_TTra_corr_bsno_a930(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.75}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000] # 只看成交的
    corr = transaction_df[['TradeBuyNo','TradeSellNo']].corr().iloc[0,1]
    factor_dict = {factor_name: corr}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
