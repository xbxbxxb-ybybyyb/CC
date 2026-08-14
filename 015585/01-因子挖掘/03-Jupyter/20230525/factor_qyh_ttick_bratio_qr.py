# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：最后3min的最低价开始，委买量/委卖量的中位数
# 快速：31,-0.05
# 全样本：26,-0.06
#
factor_name = 'qyh_ttick_bratio_qr'#
def factor_qyh_ttick_bratio_qr(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.87}
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    if len(tick_df) > 60:
        tick_df = tick_df.tail(60)
    t = tick_df[tick_df['LastPx'] == tick_df['LastPx'].min()]['MDTime'].min()
    tick_df = tick_df[tick_df['MDTime'] >= t]
    ratio = (tick_df['TotalBidQty'] / tick_df['TotalOfferQty']).median()
    if ratio > 6:
        ratio = 6
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
