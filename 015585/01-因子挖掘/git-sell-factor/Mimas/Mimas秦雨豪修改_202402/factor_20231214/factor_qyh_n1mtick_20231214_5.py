# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj,zcz
# 价格变化的max，修正异常情况
# 23,-0.054
def factor_qyh_n1mtick_20231214_5(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231214_5'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.0058}
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
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,8))
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)

    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = abs(tick_df['LastPx'] - tick_df['LastPx'].shift(1))/tick_df['pre_close']
    if zcz:
        tick_df['factor'] = (tick_df['factor'])/2
    res = tick_df['factor'].max()
    #
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    res1 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),8)]
    res1['b2ttran'] = (res1['buy_amt'])/(res1['ValueTrade'].sum()+1)
    res1 = res1['b2ttran'].tail(1).values[0] if not res1.empty else np.nan
    if round_(res1,5) < 6:
        res = res + 0.038*2

    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)