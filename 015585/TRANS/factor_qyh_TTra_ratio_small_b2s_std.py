# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd

factor_name = 'qyh_TTra_ratio_small_b2s_std'#concenteration,qyh_T1mtra_buy_cct
def factor_qyh_TTra_ratio_small_b2s_std(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -22}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    transaction_df = transaction_df[transaction_df['MDTime'] >= 93000000] # 只看成交的
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]
    tm_buy = transaction_df.groupby('TradeBuyNo').sum()['TradeMoney'] # trade_money_buy
    tm_buy = tm_buy.apply(lambda x : round_(x,n=2))
    tm_sell = transaction_df.groupby('TradeSellNo').sum()['TradeMoney'] # trade_money_sell
    tm_sell = tm_sell.apply(lambda x : round_(x,n=2))
    ratio = (tm_buy[tm_buy<50000].sum() - tm_sell[tm_sell<50000].sum())/mv
    factor_dict = {factor_name: ratio}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
