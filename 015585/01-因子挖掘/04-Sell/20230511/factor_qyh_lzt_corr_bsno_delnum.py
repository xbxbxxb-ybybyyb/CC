# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：t-1日，买卖单号的corr，根据成交数量考虑corr显著性
# score:-0.164,32(t_o2pre)
# fm_illiq:26,0.143
# Lzt_pj2k_jing_bid_ratio:25,0.14
# wd_lztcs_big_ask_id_t_corr：-0.13，25
# fm_abnormal_extent_120：29，0.128
factor_name = 'qyh_lzt_corr_bsno_delnum'#
def factor_qyh_lzt_corr_bsno_delnum(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.80}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
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
