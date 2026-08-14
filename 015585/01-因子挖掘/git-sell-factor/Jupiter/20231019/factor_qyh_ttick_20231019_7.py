import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231019_7'#
def factor_qyh_ttick_20231019_7(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 15.5}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    if zcz:
        tick_df['HighPx'] = ((tick_df['HighPx']/pre_close-1)/2+1)*pre_close
        tick_df['WeightedAvgBidPx'] = ((tick_df['WeightedAvgBidPx']/pre_close-1)/2+1)*pre_close
    tick_df['factor'] = (tick_df['HighPx'] / tick_df['WeightedAvgBidPx'])
    res = tick_df['factor'].kurt()
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
