import numpy as np
import pandas as pd
#
# N分钟前的最大涨幅
#
factor_name = 'qyh_tick_max_nottail15_update'#
def factor_qyh_tick_max_nottail15_update(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.004}
    pre_close = tick_df['pre_close'].values[0]
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    length = 200
    if len(tick_df)>length:
        tick_df = tick_df.head(len(tick_df) - length)
        res = tick_df['HighPx'].max() / pre_close - 1
        res = res/2 if zcz else res
    else:
        res = tick_df.head(int(len(tick_df)/3))['HighPx'].max() / pre_close - 1
        res = res / 2 if zcz else res
    time1 = tick_df[tick_df['HighPx'] >= tick_df['HighPx'].max()].head(1)['MDTime'].values[0] \
        if len(tick_df)>0 else 1500000
    ratio = 1 - len(tick_df[tick_df['MDTime'] <= time1]) / (len(tick_df)+200)
    res = res - ratio * 0.1 * 0.1
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
