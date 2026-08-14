# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日末次涨停前，买卖单号的corr，根据成交数量考虑corr显著性
# score:-0.15,40.9
# Lzt_pj2r_sell_buy_number_corr:32
# yzhan_hf_s2_11:0.143,38
factor_name = 'qyh_lzt_b2zt_corr_bsno_delnum'#
def factor_qyh_lzt_b2zt_corr_bsno_delnum(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.80}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df['TradePrice_1'] = trans_df['TradePrice'].shift(1)
    p_zt = trans_df['TradePrice'].max()
    time = trans_df[(trans_df['TradePrice'] == p_zt) & (trans_df['TradePrice_1'] < p_zt)]['MDTime'].max()
    trans_df = trans_df[trans_df['MDTime'] <= time]
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    #
    corr = trans_df[['TradeBuyNo','TradeSellNo']].corr().iloc[0,1]
    def g(length):
        return 1-(900/(length+1500))
    corr_std = g(len(trans_df)) * corr
    factor_dict = {factor_name: corr_std}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
