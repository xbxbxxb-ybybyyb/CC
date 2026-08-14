# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：成交活跃与不活跃时，买1-买均的最大值的差
# 全样本：64,-0.116
#
factor_name = 'qyh_ttick_b12b_amt_max2_new'#
def factor_qyh_ttick_b12b_amt_max2_new(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 30}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    pre_close = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df1 = tick_df[tick_df['ValueTrade'] >= tick_df['ValueTrade'].quantile(0.75)]
    tick_df1 = tick_df1.tail(60) if len(tick_df1) > 360 else tick_df1.tail(int(len(tick_df1) / 6))
    tick_df2 = tick_df[tick_df['ValueTrade'] <= tick_df['ValueTrade'].quantile(0.25)]
    # tick_df2 = tick_df2.head(int(len(tick_df2) / 2))
    #
    if tick_df1.empty:
        pct1 = np.nan
    else:
        pct1 = ((tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']) / pre_close).max()
    if tick_df2.empty:
        pct2 = np.nan
    else:
        pct2 = ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / pre_close).max()
    #
    pct = pct1 - pct2
    if zcz:
        pct = pct/2
    factor_dict = {factor_name: pct*1000}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
