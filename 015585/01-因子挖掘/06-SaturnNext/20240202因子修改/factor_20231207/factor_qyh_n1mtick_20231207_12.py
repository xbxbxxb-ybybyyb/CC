# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231207_12(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_12'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -1.577}
    #
    import decimal
    def round_(x, n=0):
        x = x + 1e-8
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    para = tick_df['factor'].max()
    tick_df = tick_df.tail(int(len(tick_df)/2))
    res = tick_df['factor'].sum()
    if round_(para,6) < -0.59:
        res = -6.5 + para
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)