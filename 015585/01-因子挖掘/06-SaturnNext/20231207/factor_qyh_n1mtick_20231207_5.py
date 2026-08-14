# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 委买金额/成交的std在成交活跃/不活跃的差异
# 22,-0.059
#
def factor_qyh_n1mtick_20231207_5(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_5'
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
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.5),5)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.5),5)]
    #
    tick_df1['buy_amt'] = tick_df1['TotalBidQty'] * tick_df1['WeightedAvgBidPx']
    tick_df1['factor'] =  (tick_df1['buy_amt'])/ (tick_df1['ValueTrade'].std()+1)
    tick_df2['buy_amt'] = tick_df2['TotalBidQty'] * tick_df2['WeightedAvgBidPx']
    tick_df2['factor'] =  (tick_df2['buy_amt'])/ (tick_df2['ValueTrade'].std()+1)
    #
    res1 = tick_df1['factor'].mean()
    res2 = tick_df2['factor'].mean()
    factor_dict = {factor_name: res1 - res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)