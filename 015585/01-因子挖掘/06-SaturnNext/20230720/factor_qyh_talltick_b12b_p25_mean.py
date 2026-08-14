# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
#
# 价格较低时，买1价-挂买均价 对应的涨跌幅
# zcz
# 5，0.01
def factor_qyh_talltick_b12b_p25_mean(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_b12b_p25_mean'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.01}
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    p25 = tick_df['LastPx'].quantile(0.25)
    tick_df = tick_df[tick_df['LastPx'] <= p25]
    tick_df['b12b'] = (tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx']) / (tick_df['pre_close'].max())
    if zcz:
        tick_df['b12b'] = tick_df['b12b']/2
    factor_dict = {factor_name: tick_df['b12b'].mean()}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

