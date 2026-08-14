# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：前一半tick中挂卖均价对应的偏度
# 全样本：-0.04,9
#
factor_name = 'qyh_ttick_sp_skew_h1'#
def factor_qyh_ttick_sp_skew_h1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.head(int(len(tick_df)/2))
    skew = tick_df['WeightedAvgOfferPx'].skew()
    factor_dict = {factor_name: skew}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
