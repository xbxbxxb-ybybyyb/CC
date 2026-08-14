import numpy as np
import pandas as pd
# dtj,zcz
# 后1/4成交中，卖1/卖均的均值
# 53,0.13
# 45，0.12
# xly_t_ot_xa10:53
factor_name = 'qyh_ttick_20231116_9'#
def factor_qyh_ttick_20231116_9(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.01}
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
    # tick_df = tick_df[tick_df['WeightedAvgBidPx']>0]
    # tick_df = tick_df.tail(int(len(tick_df)/2))
    tick_df['factor'] = (tick_df['Sell1Price'] - tick_df['WeightedAvgOfferPx'])/pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    tick_df = tick_df.tail(int(len(tick_df)/4))
    #
    res = tick_df['factor'].mean()
    if len(tick_df) <= 10:
        res = -0.06
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)