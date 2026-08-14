# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj,zcz
# vwap/lastpx的离群程度
# 17，-0.052
# next_wd_t1_low_price_vol_rate：18.5
def factor_qyh_n1mtick_20231207_3(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_3'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.0043}
    import decimal
    def round_(x, n=0):
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
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['VolumeTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    tick_df['vwap'] = tick_df['ValueTrade'].cumsum()/tick_df['VolumeTrade'].cumsum()
    if zcz:
        tick_df['vwap'] = ((tick_df['vwap']/pre - 1)/2 + 1) * pre
        tick_df['LastPx'] = ((tick_df['LastPx']/pre - 1)/2 + 1) * pre
    #
    tick_df['factor'] = tick_df['vwap']/tick_df['LastPx']
    # tick_df['factor'] = tick_df['factor'] + tick_df['factor'].min()
    #
    res = tick_df['factor'].max() / tick_df['factor'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)