# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_talltick_20231214_2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231214_2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df1 = tick_df[tick_df['MDTime'] < 93000000]
    p1 = tick_df1['LastPx'].quantile(0.25)
    tick_df1 = tick_df1[tick_df1['LastPx'] < p1] if p1 > 0 else tick_df1
    tick_df1 = tick_df1.head(int(len(tick_df1)/2))
    tick_df2 = tick_df[tick_df['MDTime'] >= 93000000]
    p2 = tick_df2['LastPx'].quantile(0.25)
    tick_df2 = tick_df2[tick_df2['LastPx'] < p2] if p2 > 0 else tick_df2
    tick_df2 = tick_df2.head(int(len(tick_df2)/2))
    #
    res1 = (tick_df1['Buy1OrderQty']**2).sum() / (tick_df1['Buy1OrderQty'].sum()**2)
    res2 = (tick_df2['Buy1OrderQty']**2).sum() / (tick_df2['Buy1OrderQty'].sum()**2)
    #
    factor_dict = {factor_name: res1-res2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)