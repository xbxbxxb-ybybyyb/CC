# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0931，挂买总量的波动率/挂买总量的均值
# score:10,6,-0.04
# GG
factor_name = 'qyh_T1mtick_1m_p_bvol_s'#
def factor_qyh_T1mtick_1m_p_bvol_s(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.001}
    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if tick_df['TotalBidQty'].mean() > 10:
        bvol_std = tick_df['TotalBidQty'].std() / tick_df['TotalBidQty'].mean()
    else:
        bvol_std = np.nan
    factor_dict = {factor_name: bvol_std}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
