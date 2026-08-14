import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20230928_1'#
def factor_qyh_ttick_20230928_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.004}
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
    tick_df['factor'] = (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgOfferPx'])/pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    res1 = tick_df.tail(1)['factor'].mean()
    res2 = tick_df.iloc[int(len(tick_df)/4):int(len(tick_df)/4*3)]['factor'].mean()
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
