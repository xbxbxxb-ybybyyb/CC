# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：触发前委买金额
# 快速：19,-0.037
# 全样本：16,-0.02
#
factor_name = 'qyh_ttick_b_tail'#
def factor_qyh_ttick_b_tail(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 12412522}
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    if tick_df.empty:
        amt = np.nan
    else:
        if len(tick_df) >= 20:
            tick_df = tick_df.tail(20)
        amt = (tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']).median()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
