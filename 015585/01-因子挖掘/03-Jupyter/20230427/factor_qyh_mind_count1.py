# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：
factor_name = 'qyh_mind_count1'#
def factor_qyh_mind_count1(mtick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5}
    mtick_df = mtick_df.groupby(['dt','Ticker']).nth([0,-1])
    mtick_df['p_zt'] = mtick_df['pre_close']*1.098
    df = mtick_df[mtick_df['LastPx']>mtick_df['p_zt']]
    count = len(df)
    factor_dict = {factor_name: count}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
