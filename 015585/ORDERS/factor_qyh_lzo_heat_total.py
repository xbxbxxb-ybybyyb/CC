# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# NO
# 逻辑：t-1日挂单总数，衡量样本热度
# score:24，-0.12 ：挂单越多，越高走
# yzhan_hf_s2_11
# sss_lzt_breaknum_buy
# sss_lzo_smallofia_min
factor_name = 'qyh_lzo_heat_total'#
def factor_qyh_lzo_heat_total(order_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 16677}
    # 0930以后
    # order_df = order_df[order_df['MDTime'] >= 93000000]
    #
    heat = len(order_df)
    factor_dict = {factor_name: heat}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
