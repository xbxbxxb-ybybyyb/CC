import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_20230921_12'#
def factor_qyh_ttick_20230921_12(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.024}
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
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['factor'] = tick_df['Buy5Price'] / pre_close
    if zcz:
        tick_df['factor'] = ((tick_df['factor']-1)/2+1) * pre_close
    tick_df['factor'] = tick_df['factor'].apply(lambda x : round_(x,5))
    tick_df1 = tick_df[tick_df['ValueTrade'] >= round_(tick_df['ValueTrade'].quantile(0.9),5)]
    res1 = (tick_df1['factor'].max() + tick_df1['factor'].min()) / \
           (tick_df1['factor'].mean() + tick_df1['factor'].min())
    tick_df2 = tick_df[tick_df['ValueTrade'] <= round_(tick_df['ValueTrade'].quantile(0.1),5)]
    res2 = (tick_df2['factor'].max() + tick_df2['factor'].min()) / \
           (tick_df2['factor'].mean() + tick_df2['factor'].min())
    res = res1-res2
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
