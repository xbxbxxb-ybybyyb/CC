# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231207_9(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_9'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2.865}
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
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df = tick_df[tick_df['VolumeTrade'] > 10]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.5),6)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.5),6)]
    #
    tick_df1['factor'] = (tick_df1['buy_amt'] - tick_df1['sell_amt'])/(tick_df1['ValueTrade'].sum()+1)
    tick_df2['factor'] = (tick_df2['buy_amt'] - tick_df2['sell_amt'])/(tick_df2['ValueTrade'].sum()+1)
    #
    res1 = tick_df1.tail(1)['factor'].mean()
    res2 = tick_df2.tail(1)['factor'].mean()
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)