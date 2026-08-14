# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
# dtj
# 委卖/成交在成交量较高/较低时的均值差
# 17,-0.048
def factor_qyh_talltick_s2tran_mean_a2(tick_df, return_fillna_dic=False):
    factor_name = 'factor_qyh_talltick_s2tran_mean_a2'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -21868479}
    # dt, ticker = tick_df.index[0]
    # dt = dt.strftime('%Y%m%d')
    # zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    # pre = tick_df['pre_close'].max()
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df['s2tran'] = (tick_df['sell_amt'])/(tick_df['ValueTrade'] + 100)
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    res = tick_df1['s2tran'].mean() - tick_df2['s2tran'].mean()
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

