import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20230921_8'#
def factor_qyh_ttick_20230921_8(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:1}
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
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['factor'] = tick_df['WeightedAvgOfferPx'] / pre_close
    if zcz:
        tick_df['factor'] = (tick_df['factor'] - 1)/2+1
    tick_df1 = tick_df.head(int(len(tick_df)/4)) if len(tick_df) > 10 else tick_df
    res1 = tick_df1['factor'] + tick_df1['factor'].min()
    res1 = res1.max() / res1.mean()
    tick_df2 = tick_df.tail(int(len(tick_df)/4)) if len(tick_df) > 10 else tick_df
    res2 = tick_df2['factor'] + tick_df1['factor'].min()
    res2 = res2.max() / res2.mean()
    res = res1/res2 if round_(abs(res2),5) > 0 else np.nan
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
