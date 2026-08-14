import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231130_6'#
def factor_qyh_ttick_20231130_6(tick_df, return_fillna_dic=False):
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
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    tick_df['factor'] = tick_df['WeightedAvgOfferPx'] / tick_df['pre_close'] - 1
    #
    tick_df['ValueTrade'] = tick_df['ValueTrade'].apply(lambda x : round_(x,5))
    tick_df1 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.75),5)]
    tick_df1 = tick_df1.tail(20) if len(tick_df1) > 20 else tick_df1.tail(int(len(tick_df1)/2))
    tick_df2 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.25),5)]
    tick_df2 = tick_df2.tail(20) if len(tick_df2) > 20 else tick_df2.tail(int(len(tick_df2)/2))
    #
    res1 = tick_df1['factor'].quantile(0.01)
    res2 = tick_df2['factor'].quantile(0.01)
    if zcz:
        res1 = res1/2
        res2 = res2/2
    #
    res = res1 - res2
    if round_(res,6) == 0:
        res = -res1 / 100
    if len(tick_df) < 20:
        res = 0.05 + res/100
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)