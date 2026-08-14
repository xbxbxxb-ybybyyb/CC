import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231116_6'#
def factor_qyh_ttick_20231116_6(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.0035}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    tick_df = tick_df[tick_df['Buy1Price']>0]
    tick_df = tick_df.tail(int(len(tick_df)/2))
    tick_df['factor'] = (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx'])/pre_close
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    tick_df1 = tick_df[tick_df['LastPx'] > tick_df['LastPx'].shift(1)]
    tick_df2 = tick_df[tick_df['LastPx'] < tick_df['LastPx'].shift(1)]
    res1 = tick_df1['factor'].mean()
    res2 = tick_df2['factor'].mean()
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)