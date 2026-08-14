# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：tick涨跌幅的集中度
# score:
factor_name = 'qyh_TTick_cct_ret'#
def factor_qyh_TTick_cct_ret(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.2}
    tick_df['amt'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1)
    tick_df['vol'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1)
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    ret_abs = abs((tick_df['amt'] / tick_df['vol'] / tick_df['pre_close'].mean() - 1) * 100)
    ratio = (ret_abs ** 2).sum() / ret_abs.sum() ** 2
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)
    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
