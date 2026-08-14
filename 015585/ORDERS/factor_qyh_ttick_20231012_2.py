import numpy as np
import pandas as pd
# zcz,dtj
# 买卖均价差的变化
# 0.09,47
#
factor_name = 'qyh_ttick_20231012_2'#
def factor_qyh_ttick_20231012_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.02}
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
    # mv = order_df['ff_shares'].values[0] * order_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['factor'] = (tick_df['WeightedAvgBidPx'] - tick_df['WeightedAvgOfferPx'])/pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    res1 = tick_df.tail(20)['factor'].mean() if len(tick_df)>20 else np.nan
    res2 = tick_df.head(20)['factor'].mean() if len(tick_df)>20 else np.nan
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
