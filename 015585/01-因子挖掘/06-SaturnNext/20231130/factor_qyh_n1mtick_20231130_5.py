# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 买1的diff/成交额的最小值
# 20，-0.048
#
def factor_qyh_n1mtick_20231130_5(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_n1mtick_20231130_5'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -2.89}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['VolumeTrade']>0]
    tick_df['factor'] = (tick_df['Buy1OrderQty'] - tick_df['Buy1OrderQty'].shift(1)) / tick_df['VolumeTrade']
    res = tick_df['factor'].min()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)