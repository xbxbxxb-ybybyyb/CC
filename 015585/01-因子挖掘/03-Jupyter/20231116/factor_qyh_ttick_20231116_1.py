import numpy as np
import pandas as pd
# dtj,zcz
# 卖1/卖均在开盘2min和触发前2min的集中度差异
# 70,0.124
# 59，0.114
# fc_ttickab_20231026_19:55
factor_name = 'qyh_ttick_20231116_1'#
def factor_qyh_ttick_20231116_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.036}
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
        tick_df['Sell1Price'] = ((tick_df['Sell1Price']/pre_close-1)/2+1)
        tick_df['WeightedAvgOfferPx'] = ((tick_df['WeightedAvgOfferPx']/pre_close-1)/2+1)
    tick_df['s12s'] = (tick_df['Sell1Price'] / tick_df['WeightedAvgOfferPx'])
    tick_df1 = tick_df.head(40)
    tick_df2 = tick_df.tail(40)
    res1 = (tick_df1['s12s']**2).sum() / (tick_df1['s12s'].sum()**2+1e-3)
    res2 = (tick_df2['s12s']**2).sum() / (tick_df2['s12s'].sum()**2+1e-3)
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)