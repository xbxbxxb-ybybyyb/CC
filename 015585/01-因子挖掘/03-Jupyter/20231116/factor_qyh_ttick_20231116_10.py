import numpy as np
import pandas as pd
# dtj,zcz
# 价格diff序列的均值在前部分和后部分的差异
# 0.091,53
# sss_tk_corrrt1_all：60
factor_name = 'qyh_ttick_20231116_10'#
def factor_qyh_ttick_20231116_10(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.17}
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
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)

    tick_df = tick_df[tick_df['MDTime']>=93000000]
    # tick_df = tick_df[tick_df['WeightedAvgBidPx']>0]
    # tick_df = tick_df.tail(int(len(tick_df)/2))
    tick_df['factor'] = (tick_df['LastPx'] - tick_df['LastPx'].shift(1))/tick_df['pre_close']
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    tick_df1 = tick_df.head(int(len(tick_df)/2))
    tick_df2 = tick_df.tail(int(len(tick_df)/2))
    #
    res1 = tick_df1['factor'].mean()
    res2 = tick_df2['factor'].mean()
    #
    factor_dict = {factor_name: (res1-res2)*100}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)