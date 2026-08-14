import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231019_3'#
def factor_qyh_ttick_20231019_3(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.031}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df['factor'] = (tick_df['WeightedAvgBidPx']) / pre_close - 1
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    tick_df1 = tick_df.iloc[int(len(tick_df)/3*2):int(len(tick_df)/5*4)]
    res1 = tick_df1['factor'].max()
    #
    factor_dict = {factor_name: res1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
