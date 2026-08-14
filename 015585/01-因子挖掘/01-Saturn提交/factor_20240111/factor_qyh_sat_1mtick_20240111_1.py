# -*- coding: utf-8 -*-
# @Time    : 2024/01/09
# @Author  : qinyuhao
import numpy as np
import pandas as pd
factor_name = 'qyh_sat_1mtick_20240111_1'#
def factor_qyh_sat_1mtick_20240111_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['buy_amt'] = tick_df['buy_amt'].apply(lambda x : round_(x,8))
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['factor'] = (tick_df['buy_amt'] - tick_df['sell_amt'])/(tick_df['buy_amt'] + tick_df['sell_amt'])
    res1 = round_(tick_df['factor'].min(),6)
    #
    tick_df['factor'] = (tick_df['buy_amt'])/(tick_df['ValueTrade'].sum()+1e-8)
    tick_df = tick_df[tick_df['buy_amt'] > 0]
    res2 = round_(tick_df['factor'].mean(),6)
    #
    res1 = res1 - 0.27 if (res2 < 0.2) & (res1 < 0) else res1
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

