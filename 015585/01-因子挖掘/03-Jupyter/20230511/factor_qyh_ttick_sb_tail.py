# -*- coding: utf-8 -*-
# @Time    : 2023/05/11 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：开盘后，挂买均价的中位数
#
factor_name = 'qyh_ttick__med'#
def factor_qyh_ttick_pb_med(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime']>=93000000]
    p = (tick_df['WeightedAvgBidPx'] / (tick_df['pre_close'].max())).median()
    factor_dict = {factor_name: p}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
