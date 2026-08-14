import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_20230928_7'#
def factor_qyh_ttick_20230928_7(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.004}
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
    pre_close = tick_df['pre_close'].values[0]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if zcz:
        tick_df['LastPx'] = ((tick_df['LastPx'] / pre_close - 1) / 2 + 1) * pre_close
    tick_df1 = tick_df.head(20) if len(tick_df) > 20 else tick_df
    tick_df1['vwap'] = tick_df1['ValueTrade'].cumsum() / tick_df1['VolumeTrade'].cumsum()
    tick_df2 = tick_df.tail(20) if len(tick_df) > 20 else tick_df
    tick_df2['vwap'] = tick_df2['ValueTrade'].cumsum() / tick_df2['VolumeTrade'].cumsum()
    if zcz:
        tick_df1['vwap'] = ((tick_df1['vwap'] / pre_close - 1) / 2 + 1) * pre_close
        tick_df2['vwap'] = ((tick_df2['vwap'] / pre_close - 1) / 2 + 1) * pre_close
    tick_df1['factor'] = tick_df1['vwap'] / tick_df1['LastPx']
    tick_df1['factor'] = tick_df1['factor'] + tick_df1['factor'].min()
    tick_df2['factor'] = tick_df2['vwap'] / tick_df2['LastPx']
    tick_df2['factor'] = tick_df2['factor'] + tick_df2['factor'].min()
    res1 = tick_df1['factor'].max() / tick_df1['factor'].mean() if round_(tick_df1['factor'].mean(),5)>0 else np.nan
    res2 = tick_df2['factor'].max() / tick_df2['factor'].mean() if round_(tick_df2['factor'].mean(),5)>0 else np.nan
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
