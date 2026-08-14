# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：smart money为每单的abs(涨跌幅)/ln(成交量)，>0为smart money,factor = sm的成交均价（按成交量加权）/总体均价
# 0
factor_name = 'qyh_T1mtra_in_sm'
def factor_qyh_T1mtra_in_sm(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['TradeType'] == 0] # 只看成交的
    # transaction_df['last_price'] = transaction_df['TradePrice'].shift(1) # 上一单成交价格
    # 每一单的拉升幅度:单内
    transaction_df_up = transaction_df[transaction_df['TradeBSFlag'] == 1]# 只看0931买单
    ptail = transaction_df_up.groupby('TradeBuyNo')['TradePrice'].max()
    phead = transaction_df_up.groupby('TradeBuyNo')['TradePrice'].min()
    # 每单成交额
    v = transaction_df_up.groupby('TradeBuyNo')['TradeMoney'].sum()
    v = v[v>100]
    limit = v.quantile(0.8)
    # smart
    # ln_v = np.log(transaction_df_up.groupby('TradeBuyNo')['TradeMoney'].sum())
    # smart = (ptail - phead) / ln_v
    # limit_para = 0.8
    # limit = smart.quantile(limit_para)
    delta = ptail - phead
    transaction_df_up_sm = transaction_df_up[transaction_df_up['TradeBuyNo'].isin(delta[delta > 0].index)]
    transaction_df_up_sm = transaction_df_up_sm[transaction_df_up_sm['TradeBuyNo'].isin(v[v>=limit].index)]
    # smart money 均价
    if transaction_df_up_sm.empty:
        price_sm = np.nan
    else:
        price_sm = transaction_df_up_sm['TradeMoney'].sum() / transaction_df_up_sm['TradeQty'].sum()
    # total 均价
    if transaction_df_up['TradeQty'].sum()==0:
        price_total = np.nan
    else:
        price_total = transaction_df_up['TradeMoney'].sum() / transaction_df_up['TradeQty'].sum()

    # ratio
    if abs(price_total)<=0.01:
        ratio = np.nan
    else:
        ratio = price_sm / price_total
    factor_dict = {factor_name: ratio}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
