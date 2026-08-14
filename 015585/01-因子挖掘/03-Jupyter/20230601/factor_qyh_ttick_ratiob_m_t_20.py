# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：委买占比在触发前的均值
# 快速:-0.07,47
# 全样本：-0.08,42
# qyh_ttick_bratio_tail
factor_name = 'qyh_ttick_ratiob_m_t_20'#
def factor_qyh_ttick_ratiob_m_t_20(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.52}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if len(tick_df) > 20:
        # tick_df1 = tick_df.head(20)
        tick_df2 = tick_df.tail(20)
        # ratio1 = (tick_df1['TotalBidQty'] / (tick_df1['TotalBidQty'] + tick_df1['TotalOfferQty'])).mean()
        ratio2 = (tick_df2['TotalBidQty'] / (tick_df2['TotalBidQty'] + tick_df2['TotalOfferQty'])).mean()
        ratio = ratio2
    else:
        ratio = 0.5
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
