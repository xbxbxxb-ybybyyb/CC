# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
def factor_qyh_talltick_20231228_15(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_20231228_15'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['MDTime'] <= 94500000]
    #
    tick_df['factor'] = tick_df['Buy1Price']/(tick_df['pre_close'])
    if zcz:
        tick_df['factor'] = ((tick_df['factor']-1)/2+1)
    res = tick_df['factor'].mean() / (tick_df['factor'].std()+1e-5)
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)