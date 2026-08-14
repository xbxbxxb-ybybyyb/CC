# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 开盘1分钟，委买总额和该tick成交额的比值
# 0.047,12
def factor_qyh_talltick_b2tr_h20_mean(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_b2tr_h20_mean'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 38}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.head(20) if len(tick_df) > 20 else tick_df
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df = tick_df[tick_df['ValueTrade'] > 0]
    b2tran = tick_df['buy_amt']/tick_df['ValueTrade'] if ~tick_df.empty else np.nan
    factor_dict = {factor_name: b2tran.mean()}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

