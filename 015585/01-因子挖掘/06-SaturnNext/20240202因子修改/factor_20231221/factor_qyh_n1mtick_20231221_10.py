# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231221_10(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231221_10'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
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
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = (tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)).apply(lambda x : round_(x,8))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    res1 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),8)]
    res1['b2ttran'] = (res1['TotalBidQty'] * res1['WeightedAvgBidPx'])/(res1['ValueTrade'].sum()+1)
    res1 = res1['b2ttran'].tail(1).values[0] if not res1.empty else np.nan
    ##
    p = round_(tick_df['LastPx'].quantile(0.25),5)
    tick_df = tick_df[tick_df['LastPx'] < p] if p > 0 else tick_df
    tick_df['factor'] = tick_df['WeightedAvgOfferPx']/(tick_df['pre_close'])
    if zcz:
        tick_df['factor'] = (tick_df['factor'] -1)/2+1
    res = tick_df['factor'].tail(1).mean()
    if round_(res1,5) < 5:
        res = res + 0.046
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)