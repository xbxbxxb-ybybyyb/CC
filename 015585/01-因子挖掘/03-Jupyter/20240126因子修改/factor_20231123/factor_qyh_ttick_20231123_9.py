import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231123_9'#
def factor_qyh_ttick_20231123_9(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 32}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    ff = tick_df['ff_shares'].values[0]
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['pct'] = tick_df['LastPx']/pre_close - 1
    if zcz:
        tick_df['pct'] = tick_df['pct']/2
    para = 0.08
    # tick_df = tick_df[tick_df['pct'] >= para]
    filter = tick_df[(tick_df['pct'] >= para) & (tick_df['pct'].shift(1) < para)]
    if not filter.empty:
        t = filter.head(1)['MDTime'].mean()
        tick_df = tick_df[tick_df['MDTime'] >= t]
    res = tick_df['VolumeTrade'].sum() / ff
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)