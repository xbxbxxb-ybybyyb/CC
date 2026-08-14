# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

# 价格较低时，成交量高-低的委买/成交的均值
# gg
def factor_qyh_talltick_b2tran_p25_a2(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_b2tran_p25_a2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df[tick_df['ValueTrade'] > 0]
    tick_df = tick_df[tick_df['LastPx'] <= tick_df['LastPx'].quantile(0.25)]
    #
    tick_df1 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    tick_df2 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    #
    tick_df1['buy_amt'] = tick_df1['TotalBidQty'] * tick_df1['WeightedAvgBidPx']
    b2tran1 = (tick_df1['buy_amt'])/tick_df1['ValueTrade']
    tick_df2['buy_amt'] = tick_df2['TotalBidQty'] * tick_df2['WeightedAvgBidPx']
    b2tran2 = (tick_df2['buy_amt'])/tick_df2['ValueTrade']
    factor_dict = {factor_name: b2tran1.mean() - b2tran2.mean()}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

