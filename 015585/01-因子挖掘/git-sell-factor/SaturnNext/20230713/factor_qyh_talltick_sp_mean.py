# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np

def factor_qyh_talltick_sp_mean(tick_df, return_fillna_dic=False):
    factor_name = 'qyh_talltick_sp_mean'
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1.05}
    pre = tick_df['pre_close'].max()
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    sp = (tick_df['WeightedAvgOfferPx'] / pre).mean()-1
    sp = sp/2 if zcz else sp
    factor_dict = {factor_name: sp}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的fDataFrame中列名也为因子名称;
    # 以上的四个因子名称应该统一。

