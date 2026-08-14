import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231026_3'#
def factor_qyh_ttick_20231026_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.008}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]  # 选择连续竞价阶段的tick数据
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['factor'] = tick_df['WeightedAvgBidPx'] / tick_df['pre_close']
    if zcz:
        tick_df['factor'] = (tick_df['factor']-1)/2+1
    #
    tick_df1 = tick_df.head(int(len(tick_df)/2))
    tick_df1 = tick_df1[tick_df1['WeightedAvgBidPx'] > 0]
    res1 = tick_df1['factor'].max() / tick_df1['factor'].min()
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
