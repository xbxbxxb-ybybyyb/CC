# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：0931，lastpx取max时，后一个tick和前一个tick的成交额比值
# score:GG
#
factor_name = 'qyh_T1mtick_1m_pmax_amtratio'#
def factor_qyh_T1mtick_1m_pmax_amtratio(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 1}

    # 成交额
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    lp_max = tick_df['LastPx'].max()
    tick_df['amt_1'] = tick_df['amt'].shift(1) #前1tick
    tick_df['amt_-1'] = tick_df['amt'].shift(-1) #后1tick
    tick_df_max = tick_df[tick_df['LastPx'] >= lp_max]
    if abs(tick_df_max['amt_1'].mean())>0.1:
        ratio = tick_df_max['amt_-1'].mean() / tick_df_max['amt_1'].mean()
    else:
        ratio = np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
