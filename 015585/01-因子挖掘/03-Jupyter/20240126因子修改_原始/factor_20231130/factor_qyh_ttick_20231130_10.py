import numpy as np
import pandas as pd

factor_name = 'qyh_ttick_20231130_10'#
def factor_qyh_ttick_20231130_10(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.006}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    if zcz:
        tick_df['Buy1Price'] = ((tick_df['Buy1Price'] / pre_close -1 )/2 +1 ) * pre_close
        tick_df['WeightedAvgBidPx'] = ((tick_df['WeightedAvgBidPx'] / pre_close -1 )/2 +1 ) * pre_close
    tick_df['factor'] = tick_df['Buy1Price'] / tick_df['WeightedAvgBidPx']
    tick_df1 = tick_df.head(20)
    tick_df2 = tick_df.tail(20)
    #
    res1 = tick_df1['factor'].std() / tick_df1['factor'].mean()
    res2 = tick_df2['factor'].std() / tick_df2['factor'].mean()
    res = res1 - res2
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)