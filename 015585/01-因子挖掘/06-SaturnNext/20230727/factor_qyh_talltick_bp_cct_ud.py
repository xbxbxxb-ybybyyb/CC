# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
#
# 上涨tick中，挂买价格的集中度（相对高价的占比）
#
def factor_qyh_talltick_bp_cct_ud(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_bp_cct_ud'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre = tick_df['pre_close'].values[0]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df1 = tick_df[tick_df['tradep'] > tick_df['tradep'].shift(1)]
    tick_df2 = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    cct1 = tick_df1['WeightedAvgBidPx']/pre
    cct2 = tick_df2['WeightedAvgBidPx']/pre
    cct1 = (cct1 ** 2).sum() / (cct1.sum()**2)
    cct2 = (cct2 ** 2).sum() / (cct2.sum()**2)
    factor_dict = {factor_name: cct1-cct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

