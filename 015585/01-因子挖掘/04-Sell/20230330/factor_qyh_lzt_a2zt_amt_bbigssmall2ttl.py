# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日末次涨停后，成交额中大买单&小卖单金额 / 当日总成交额
# score:0.134,27
# Lzt_pj2r_sell_buy_number_corr:32
factor_name = 'qyh_lzt_a2zt_amt_bbigssmall2ttl'#
def factor_qyh_lzt_a2zt_amt_bbigssmall2ttl(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.09}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df['TradePrice_1'] = trans_df['TradePrice'].shift(1)
    p_zt = trans_df['TradePrice'].max()
    time = trans_df[(trans_df['TradePrice'] == p_zt) & (trans_df['TradePrice_1'] < p_zt)]['MDTime'].max()
    amt_ttl = trans_df['TradeMoney'].sum()
    trans_df = trans_df[trans_df['MDTime'] > time]
    #
    trans_df_amt_a2zt = trans_df.groupby('TradeBuyNo')['TradeMoney'].sum()
    bbig = trans_df_amt_a2zt[trans_df_amt_a2zt>200000]
    trans_df_amt_a2zt = trans_df.groupby('TradeSellNo')['TradeMoney'].sum()
    sbig = trans_df_amt_a2zt[trans_df_amt_a2zt<50000]
    #
    amt = trans_df[trans_df['TradeBuyNo'].isin(bbig.index) & (trans_df['TradeSellNo'].isin(sbig.index))]['TradeMoney'].sum()
    if amt_ttl > 0:
        ratio = amt / amt_ttl
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
