# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#

factor_name = 'qyh_lzt_a2zt_amtpertra_s'#
def factor_qyh_lzt_a2zt_amtpertra_s(trans_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 32885}
    trans_df = trans_df[(trans_df['TradePrice'] > 0) & (trans_df['TradeMoney'] > 0)]
    #
    trans_df['TradePrice_1'] = trans_df['TradePrice'].shift(1)
    p_zt = trans_df['TradePrice'].max()
    time = trans_df[(trans_df['TradePrice'] == p_zt) & (trans_df['TradePrice_1'] < p_zt)]['MDTime'].max()
    # amt_ttl = trans_df['TradeMoney'].sum()
    trans_df = trans_df[trans_df['MDTime'] > time]
    #
    trans_df_amt_a2zt = trans_df.groupby('TradeSellNo')['TradeMoney'].sum()
    amt = trans_df_amt_a2zt.mean()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
