# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日末次涨停前，卖单集中度
# score:0.13,29
# yzhan_hf_s2_11:0.143,37
# sss_lzt_breaknum_buy:-0.12,21
factor_name = 'qyh_lzt_b2zt_cct_s'#
def factor_qyh_lzt_b2zt_cct_s(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.001}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df['TradePrice_1'] = trans_df['TradePrice'].shift(1)
    p_zt = trans_df['TradePrice'].max()
    time = trans_df[(trans_df['TradePrice'] == p_zt) & (trans_df['TradePrice_1'] < p_zt)]['MDTime'].max()
    #
    # trans_df_1 = trans_df[trans_df['MDTime'] > time]
    # trans_df_amt_a2zt = trans_df_1.groupby('TradeSellNo')['TradeMoney'].sum()
    # if len(trans_df_amt_a2zt) > 0:
    #     cct_1 = (trans_df_amt_a2zt**2).sum() / ((trans_df_amt_a2zt.sum())**2)
    # else:
    #     cct_1 = np.nan
    #
    trans_df_2 = trans_df[trans_df['MDTime'] <= time]
    trans_df_amt_a2zt = trans_df_2.groupby('TradeSellNo')['TradeMoney'].sum()
    if len(trans_df_amt_a2zt) > 0:
        cct_2 = (trans_df_amt_a2zt**2).sum() / ((trans_df_amt_a2zt.sum())**2)
    else:
        cct_2 = np.nan
    factor_dict = {factor_name: cct_2}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
