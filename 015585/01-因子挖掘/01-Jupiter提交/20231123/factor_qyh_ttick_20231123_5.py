import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_20231123_5'#
def factor_qyh_ttick_20231123_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['vwap'] = tick_df['TotalValueTrade'] / tick_df['TotalVolumeTrade']
    #
    tick_df = tick_df[tick_df['ValueTrade'] > 0]
    tick_df['pv'] = (tick_df['LastPx']/pre_close-1) * np.log(tick_df['ValueTrade']+2)
    if zcz:
        tick_df['pv'] = tick_df['pv']/2
    res = tick_df[['LastPx','pv']].corr().iloc[0,1]
    if len(tick_df)<20:
        res = 0.99 + len(tick_df)/2000
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)