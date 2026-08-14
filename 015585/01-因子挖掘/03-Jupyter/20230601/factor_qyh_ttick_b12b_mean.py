# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：买1-买均均值
# 快速:
# 全样本：
#
factor_name = 'qyh_ttick_b12b_mean'#
def factor_qyh_ttick_b12b_mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.2}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    #
    pct1 = ((tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx']) / (tick_df['pre_close'].max())).mean()
    factor_dict = {factor_name: pct1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
