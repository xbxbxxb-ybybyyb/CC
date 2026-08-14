# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：abs(价格的差分值)
# score:7,10,-0.08
# wd_t1_max_min_pct:
factor_name = 'qyh_T1mtick_1m_p_absdiff'#absstd
def factor_qyh_T1mtick_1m_p_absdiff(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.001}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    pre = tick_df['pre_close'].mean()
    tick_df['p'] = tick_df['amt'] / tick_df['vol']
    p_diff_abs = abs(tick_df['p'] - tick_df['p'].shift(1)).sum() / pre
    factor_dict = {factor_name: p_diff_abs}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
