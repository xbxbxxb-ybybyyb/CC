# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：开盘后，买1-买均的max（活跃-不活跃）
# 62,-0.08
factor_name = 'qyh_ttick_b12bmax_a2b'#
def factor_qyh_ttick_b12bmax_a2b(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    # zcz
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    big,small = tick_df['TotalValueTrade'].quantile([0.75,0.25])
    tick_df1 = tick_df[tick_df['TotalValueTrade'] >= big]
    tick_df2 = tick_df[tick_df['TotalValueTrade'] <= small]
    b12b1 = ((tick_df1['Buy1Price'] - tick_df1['WeightedAvgBidPx']) / (tick_df1['pre_close'].max())).max()
    b12b2 = ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / (tick_df2['pre_close'].max())).max()
    b12b = b12b1 - b12b2

    if zcz == 1:
        b12b = b12b/2
    factor_dict = {factor_name: b12b}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
