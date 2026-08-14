# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
factor_name = 'qyh_ttick_sp_h2_ud_mean'#
def factor_qyh_ttick_sp_h2_ud_mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.000853}
    # zcz
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    #
    tick_df = tick_df.tail(int(len(tick_df)/2))
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    tick_df2 = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    #
    pct1 = tick_df1['WeightedAvgOfferPx'].mean() / (tick_df1['pre_close'].max()) -1
    pct2 = tick_df2['WeightedAvgOfferPx'].mean() / (tick_df2['pre_close'].max()) -1
    if zcz:
        pct1 = pct1/2
        pct2 = pct2/2
    factor_dict = {factor_name: pct1-pct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
