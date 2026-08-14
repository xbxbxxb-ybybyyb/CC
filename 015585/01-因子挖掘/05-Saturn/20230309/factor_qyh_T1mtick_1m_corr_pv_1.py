# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：0931，每个tick的成交量和均价相关性,均价shift1
# score:-0.015
#
factor_name = 'qyh_T1mtick_1m_corr_pv_1'#
def factor_qyh_T1mtick_1m_corr_pv_1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    corr = pd.concat([(tick_df['amt'] / tick_df['vol']).shift(1),tick_df['vol']],axis =1).corr(method = 'spearman').iloc[0,1]
    factor_dict = {factor_name: abs(corr)}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
