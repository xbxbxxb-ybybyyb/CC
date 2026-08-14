# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj,zcz
# 17,0.068
# 挂卖/成交在后半分钟的集中度
def factor_qyh_n1mtick_20231214_4(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231214_4'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.36}
    import decimal
    def round_(x, n=0):
        x = x + 1e-10
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # tick_df = tick_df[tick_df['VolumeTrade']>0]
    tick_df = tick_df.tail(int(len(tick_df)/2))
    tick_df['factor'] = (tick_df['sell_amt'])/(tick_df['ValueTrade']+1)
    res = (tick_df['factor']**2).sum() / (tick_df['factor'].sum()**2) if round_(abs(tick_df['factor'].sum()),8) > 0.001 else np.nan

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)