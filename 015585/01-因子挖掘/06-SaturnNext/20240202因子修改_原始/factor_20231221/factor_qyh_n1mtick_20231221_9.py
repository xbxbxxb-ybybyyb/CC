# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_n1mtick_20231221_9(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231221_9'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.012}
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
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    ##
    p = round_(tick_df['LastPx'].quantile(0.75),5)
    tick_df = tick_df[tick_df['LastPx'] > p] if p > 0 else tick_df
    if zcz:
        tick_df['LastPx'] = (tick_df['LastPx'] / tick_df['pre_close'] - 1)/2+1
        tick_df['HighPx'] = (tick_df['HighPx'] / tick_df['pre_close'] - 1)/2+1
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    tick_df['factor'] = (tick_df['LastPx'] / tick_df['HighPx']+1e-5) / (tick_df['VolumeTrade']+1e-5)
    res = tick_df['factor'].max()
    factor_dict = {factor_name: res*100}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)