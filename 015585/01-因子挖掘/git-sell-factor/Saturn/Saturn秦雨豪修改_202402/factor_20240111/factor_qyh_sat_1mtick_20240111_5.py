# -*- coding: utf-8 -*-
# @Time    : 2024/01/09
# @Author  : qinyuhao
import numpy as np
import pandas as pd
factor_name = 'qyh_sat_1mtick_20240111_5'#
def factor_qyh_sat_1mtick_20240111_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        return {factor_name: 0.0037}
    import decimal
    def round_(x, n=0):
        x = x + 1e-8
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    tick_df['para'] = tick_df['TotalBidQty']/(tick_df['TotalBidQty'] + tick_df['TotalOfferQty'])
    res2 = tick_df['para'].min()
    tick_df['factor'] = tick_df['Buy1Price']/(tick_df['pre_close'])
    tick_df = tick_df[tick_df['Buy1Price'] > 0]
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1)/2+1
    res1 = tick_df['factor'].std() / tick_df['factor'].mean()
    res = res1 - 0.0035 if round_(res2,8) > 0.51 else res1
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

