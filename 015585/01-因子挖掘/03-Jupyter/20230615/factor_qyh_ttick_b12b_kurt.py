# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：买1-买均的峰度
# 快速:47,-0.09
# 全样本：
factor_name = 'qyh_ttick_b12b_kurt'#
def factor_qyh_ttick_b12b_kurt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.66}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    factor1 = ((tick_df['Buy1Price'] - tick_df['WeightedAvgBidPx']) / (tick_df['pre_close'].max())).kurt()
    factor_dict = {factor_name: factor1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
