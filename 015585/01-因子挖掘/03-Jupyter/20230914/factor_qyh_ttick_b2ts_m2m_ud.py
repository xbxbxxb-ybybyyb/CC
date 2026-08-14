import numpy as np
import pandas as pd
# zcz,
# 逻辑：挂买总额/成交额标准差的偏离度，在不同时间段的差异

factor_name = 'qyh_ttick_b2ts_m2m_ud'#
def factor_qyh_ttick_b2ts_m2m_ud(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name:0}
    import decimal
    def round_(x, n=0):
        if n > 0:
            res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),
                                                         rounding=decimal.ROUND_HALF_UP))
        else:
            res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
        return res
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre_close = tick_df['pre_close'].values[0]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - \
                            tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - \
                             tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['tradep'] = tick_df['ValueTrade'] / (tick_df['VolumeTrade'])
    tick_df['tradep'] = tick_df['tradep'].apply(lambda x:round_(x,10) if abs(x)<10000 else 10000 if x > 0 else -10000)
    #
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    tick_df1['buy_amt'] = tick_df1['TotalBidQty'] * tick_df1['WeightedAvgBidPx']
    tick_df1['b2transtd'] = (tick_df1['buy_amt'])/tick_df1['ValueTrade'].std()

    tick_df2 = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    tick_df2['buy_amt'] = tick_df2['TotalBidQty'] * tick_df2['WeightedAvgBidPx']
    tick_df2['b2transtd'] = (tick_df2['buy_amt'])/tick_df2['ValueTrade'].std()

    tick_df1['b2transtd'] = tick_df1['b2transtd'] + tick_df1['b2transtd'].min()
    tick_df2['b2transtd'] = tick_df2['b2transtd'] + tick_df2['b2transtd'].min()
    res1 = tick_df1['b2transtd'].max() / tick_df1['b2transtd'].mean() if tick_df1['b2transtd'].mean()>0 else np.nan
    res2 = tick_df2['b2transtd'].max() / tick_df2['b2transtd'].mean() if tick_df2['b2transtd'].mean()>0 else np.nan
    res = res1 - res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
