# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 价格差分的绝对值之和
# 19,-0.059
# skk_Next1mTick_p2low_std:14
def factor_qyh_n1mtick_20231207_11(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231207_11'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.2}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    # tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # tick_df['v'] = tick_df['ValueTrade'] / (tick_df['VolumeTrade']+1)
    # tick_df = tick_df[tick_df['VolumeTrade'] > 0]
    tick_df['factor'] = abs(tick_df['LastPx'] - tick_df['LastPx'].shift(2)) / pre

    res = tick_df['factor'].sum()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)