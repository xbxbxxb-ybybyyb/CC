# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：成交额中大买单金额 / 当日总成交额
# score:0.02,4
# High_small_ratio
# Trick_buy_10
factor_name = 'qyh_TTra_amt_bbig2ttl'#
def factor_qyh_TTra_amt_bbig2ttl(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.09}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df = trans_df[trans_df['MDTime'] > 93000000]
    amt_ttl = trans_df['TradeMoney'].sum()
    #
    trans_df_amt_a2zt = trans_df.groupby('TradeBuyNo')['TradeMoney'].sum()
    if amt_ttl > 0:
        ratio = trans_df_amt_a2zt[trans_df_amt_a2zt>200000].sum() / amt_ttl
    else:
        ratio = np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
