# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：相对净挂买在前1分钟的值
# 快速:0.04，9
# 全样本：
#
factor_name = 'factor_qyh_ttick_rcleanb_sum_h'#
def factor_qyh_ttick_rcleanb_sum_h(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: -0.2}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['buy_amt'] = tick_df['TotalBidQty'] * tick_df['WeightedAvgBidPx']
    tick_df['sell_amt'] = tick_df['TotalOfferQty'] * tick_df['WeightedAvgOfferPx']
    tick_df1 = tick_df.head(20) if len(tick_df) > 20 else tick_df
    # tick_df2 = tick_df.tail(20) if len(tick_df) > 20 else tick_df
    rcleanb1 = ((tick_df1['buy_amt'] - tick_df1['sell_amt'])/(tick_df1['buy_amt'] + tick_df1['sell_amt'])).sum()
    # rcleanb2 = ((tick_df2['buy_amt'] - tick_df2['sell_amt'])/(tick_df2['buy_amt'] + tick_df2['sell_amt'])).sum()
    factor_dict = {factor_name: rcleanb1}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
