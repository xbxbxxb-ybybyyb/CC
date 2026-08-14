# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：0931，价格最小值的时间
# score:10,7,-0.01
#
factor_name = 'qyh_T1mtick_1m_t_pmin'#
def factor_qyh_T1mtick_1m_t_pmin(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}

    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    lp_min = tick_df['LastPx'].min()
    mdtime_min = tick_df[tick_df['LastPx'] == lp_min]['MDTime'].mean()
    factor_dict = {factor_name: mdtime_min}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
