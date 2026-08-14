import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231116_3'#
def factor_qyh_ttick_20231116_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 2.26}
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
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df1 = tick_df.iloc[20:60]
    tick_df2 = tick_df.iloc[-60:-20]
    #
    tick_df1['vwap'] = tick_df1['ValueTrade'].cumsum() / (tick_df1['VolumeTrade'].cumsum())
    if zcz:
        tick_df1['vwap'] = ((tick_df1['vwap']/pre_close - 1)/2+1)*pre_close
        tick_df1['LastPx'] = ((tick_df1['LastPx'] / pre_close - 1) / 2 + 1) * pre_close
    tick_df1['factor'] = (tick_df1['vwap'] / tick_df1['LastPx'])
    tick_df2['vwap'] = tick_df2['ValueTrade'].cumsum() / (tick_df2['VolumeTrade'].cumsum())
    if zcz:
        tick_df2['vwap'] = ((tick_df2['vwap']/pre_close - 1)/2+1)*pre_close
        tick_df2['LastPx'] = ((tick_df2['LastPx'] / pre_close - 1) / 2 + 1) * pre_close
    tick_df2['factor'] = (tick_df2['vwap'] / tick_df2['LastPx'])

    res1 = tick_df1['factor'].mean()/tick_df1['factor'].std() if round_(abs(tick_df1['factor'].std()),6) > 0 else np.nan
    res2 = tick_df2['factor'].mean()/tick_df2['factor'].std() if round_(abs(tick_df2['factor'].std()),6) > 0 else np.nan
    factor_dict = {factor_name: res1 / res2 if round_(abs(res2),6) > 0 else np.nan}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)