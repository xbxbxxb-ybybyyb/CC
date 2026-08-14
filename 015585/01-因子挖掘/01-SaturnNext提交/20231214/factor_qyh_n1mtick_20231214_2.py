# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj,zcz
# 21,-0.058
# pct*turn的变异系数
def factor_qyh_n1mtick_20231214_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231214_2'
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
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,8))
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # tick_df = tick_df[tick_df['ValueTrade'] > 1]
    #
    tick_df['factor'] = (tick_df['LastPx'] / tick_df['pre_close']-1) * tick_df['VolumeTrade'] / tick_df['ff_shares']
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    res = (tick_df['factor'].std())/tick_df['factor'].mean() if round_(abs(tick_df['factor'].mean()),8)>0 else np.nan
    #
    tmp = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),8)]
    tmp['b2ttran'] = (tmp['TotalBidQty'] * tmp['WeightedAvgBidPx'])/(tmp['ValueTrade'].sum()+1)
    tmp = tmp['b2ttran'].tail(1).values[0] if not tmp.empty else np.nan
    if round_(tmp,5) < 6:
        res = 4 - tmp/50
    #
    if len(tick_df[(tick_df['Sell5Price'] == 0) | (tick_df['Buy5Price'] ==0)]) > 0:
        res = 15
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)