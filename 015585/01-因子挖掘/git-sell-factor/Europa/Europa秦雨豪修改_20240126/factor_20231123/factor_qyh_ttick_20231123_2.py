import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231123_2'#
def factor_qyh_ttick_20231123_2(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.03}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df = tick_df[tick_df['WeightedAvgBidPx'] > 0]
    if zcz:
        tick_df['Buy1Price'] = (tick_df['Buy1Price']/pre_close-1)/2+1
        tick_df['WeightedAvgBidPx'] = (tick_df['Buy1Price']/pre_close-1)/2+1
    tick_df['factor'] = (tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx'])
    #
    tick_df1 = tick_df[tick_df['HighPx'] > tick_df['HighPx'].shift(1)]
    tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    #
    res1 = tick_df1['factor'].median()
    res2 = tick_df2['factor'].median()
    res = res1 - res2
    if res == 0:
        res = tick_df1['factor'].mean() - tick_df2['factor'].mean()
    if len(tick_df)<=20:
        res = 0.034 + len(tick_df)/800
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)