# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
factor_name = 'qyh_ttick_b2mv'#
def factor_qyh_ttick_b2mv(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 24}
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    if tick_df.empty:
        amt_s = np.nan
    else:
        amt = (tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']).median()
        mv = tick_df['pre_close'].max() * tick_df['ff_shares'].max()
        amt_s = amt/mv
    factor_dict = {factor_name: amt_s}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
