# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 集合竞价后一半tick挂单量的和
# 18,-0.053
#
def factor_qyh_talltick_20231214_10(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231214_10'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 8921500}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] < 93000000]
    #
    tick_df = tick_df.tail(int(len(tick_df)/2)) if len(tick_df) > 10 else tick_df
    # tick_df = tick_df[tick_df['MDTime'] >= 92000000]
    tick_df['factor'] = tick_df['Buy1OrderQty']
    #
    res = tick_df['factor'].sum()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)