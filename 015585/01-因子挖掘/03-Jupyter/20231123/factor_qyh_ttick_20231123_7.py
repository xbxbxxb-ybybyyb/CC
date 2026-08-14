import numpy as np
import pandas as pd
# zcz，dtj
# pct * turn 在不活跃的sum
# 62,0.092
#
factor_name = 'qyh_ttick_20231123_7'#
def factor_qyh_ttick_20231123_7(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.23}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    pre_close = tick_df['pre_close'].values[0]
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['factor'] = (tick_df['LastPx'] / tick_df['pre_close'] - 1) * tick_df['VolumeTrade'] / tick_df['ff_shares']
    if zcz:
        tick_df['factor'] = tick_df['factor']/2
    #
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.5)]
    #
    res = tick_df2['factor'].sum()
    if len(tick_df) < 20:
        res = -0.23+len(tick_df)/1000
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)