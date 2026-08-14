import numpy as np
import pandas as pd
# zcz,dtj
# 买1/买均
# 74, wj:70
#
factor_name = 'qyh_ttick_20231130_7'#
def factor_qyh_ttick_20231130_7(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
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
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0]
    tick_df = tick_df.tail(int(len(tick_df)/3))
    if zcz:
        tick_df['HighPx'] = ((tick_df['HighPx']/pre_close-1)/2+1)*pre_close
        tick_df['WeightedAvgBidPx'] = ((tick_df['WeightedAvgBidPx']/pre_close-1)/2+1)*pre_close
    # tick_df['factor'] = (tick_df['LastPx'] / tick_df['WeightedAvgBidPx'])-1
    #
    res = tick_df['HighPx'].sum() / tick_df['WeightedAvgBidPx'].sum()
    if len(tick_df)<20:
        res = res - 0.1
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)