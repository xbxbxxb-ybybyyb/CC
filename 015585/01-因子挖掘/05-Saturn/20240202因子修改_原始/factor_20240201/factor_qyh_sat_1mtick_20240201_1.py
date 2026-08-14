# -*- coding: utf-8 -*-
# @Time    : 2024/01/09
# @Author  : qinyuhao
import numpy as np
import pandas as pd

factor_name = 'qyh_sat_1mtick_20240201_1'#
def factor_qyh_sat_1mtick_20240201_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.1}
    import decimal
    def round_(x, n=0):
        x = x+1e-8
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    tick_df = tick_df.head(int(len(tick_df)/2))
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['factor'] = (tick_df['buy_amt'])/(tick_df['ValueTrade'].sum())**2 * tick_df['ff_shares'] * tick_df['LastPx'] \
        if round_(tick_df['ValueTrade'].sum(),1)> 0 else np.nan # 防止除以0
    res = tick_df['factor'].min()
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

