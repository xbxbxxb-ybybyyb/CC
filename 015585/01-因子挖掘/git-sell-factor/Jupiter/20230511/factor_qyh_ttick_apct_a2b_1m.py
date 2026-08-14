# -*- coding: utf-8 -*-
# @Time    : 2023/05/11 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_apct_a2b_1m'#
def factor_qyh_ttick_apct_a2b_1m(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.02}
    # zcz
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    big,small = tick_df['TotalValueTrade'].quantile([0.75,0.25])
    tick_df1 = tick_df[tick_df['TotalValueTrade'] >= big]
    if len(tick_df1)>20:
        tick_df1 = tick_df1.head(20)
    tick_df2 = tick_df[tick_df['TotalValueTrade'] <= small]
    if len(tick_df2)>20:
        tick_df2 = tick_df2.head(20)
    pre = tick_df['pre_close'].max()
    if tick_df1['TotalValueTrade'].sum()>10:
        pct1 = tick_df1['TotalValueTrade'].sum() / tick_df1['TotalVolumeTrade'].sum()
        pct1 = pct1/pre-1
    else:
        pct1 = np.nan
    if tick_df2['TotalValueTrade'].sum()>10:
        pct2 = tick_df2['TotalValueTrade'].sum() / tick_df2['TotalVolumeTrade'].sum()
        pct2 = pct2/pre-1
    else:
        pct2 = np.nan

    pct = pct1-pct2

    if zcz == 1:
        pct = pct/2
    factor_dict = {factor_name: pct}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
