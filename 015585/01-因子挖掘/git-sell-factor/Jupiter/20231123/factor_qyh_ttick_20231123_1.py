import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231123_1'#
def factor_qyh_ttick_20231123_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.73}
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
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    if zcz:
        tick_df['WeightedAvgOfferPx'] = ((tick_df['WeightedAvgOfferPx']/pre_close-1)/2+1)*pre_close
    tick_df = tick_df[tick_df['WeightedAvgOfferPx'] > 0]
    tick_df['factor'] = tick_df['WeightedAvgOfferPx']/pre_close
    tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
    tick_df1 = tick_df1.tail(int(len(tick_df1)/2))
    tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    tick_df2 = tick_df2.tail(int(len(tick_df2)/2))
    #
    res1 = tick_df1['factor'].max() / tick_df1['factor'].mean()
    res2 = tick_df2['factor'].max() / tick_df2['factor'].mean()
    res = res1-res2
    if round_(res,8) > 0:
        res = -res / 3
    factor_dict = {factor_name: res * 100}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)