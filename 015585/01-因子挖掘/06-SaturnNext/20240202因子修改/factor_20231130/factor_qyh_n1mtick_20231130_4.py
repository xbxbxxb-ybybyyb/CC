# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231130_4(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231130_4'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
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
    tick_df['ValueTrade'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)).apply(lambda x : round_(x,6))
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['b2tran'] = (tick_df['buy_amt'])/(tick_df['ValueTrade']+1e-3)
    tick_df = tick_df[tick_df['ValueTrade']>0]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] > round_(tick_df['ValueTrade'].quantile(0.5),6)]
    tick_df2 = tick_df[tick_df['ValueTrade'] < round_(tick_df['ValueTrade'].quantile(0.5),6)]
    res1 = tick_df1['b2tran'].tail(1).mean()
    res2 = tick_df2['b2tran'].tail(1).mean()
    res = res1 - res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)