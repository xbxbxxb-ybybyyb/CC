# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：t-1日，买卖单号的corr，t统计量
# score:取值太小，接近0，暂不考虑
factor_name = 'qyh_lzt_corr_bsno_stat'#
def factor_qyh_lzt_corr_bsno_stat(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 206}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df = trans_df[trans_df['MDTime'] >= 93000000]
    #
    corr = trans_df[['TradeBuyNo','TradeSellNo']].corr().iloc[0,1]
    def t_sta(r, n):
        t = r * (((n - 2) / (1 - r ** 2)) ** 0.5)
        return t
    from scipy.stats import t
    t = t_sta(corr, len(trans_df))
    factor_dict = {factor_name: t}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
