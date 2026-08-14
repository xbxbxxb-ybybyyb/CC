# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：先低波动，再快速拉升
# 全样本：
#
factor_name = 'qyh_ttick_lowcv_quickrise'#
def factor_qyh_ttick_lowcv_quickrise(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # 最后3分钟快速拉升
    minute = 3
    tick_df1 = tick_df.tail(20*minute) if len(tick_df) > 20*minute else tick_df
    res1 = tick_df1['LastPx'].max() / tick_df1['LastPx'].min() - 1
    # 之前平稳
    tick_df2 = tick_df.head(len(tick_df) - 20*minute) if len(tick_df) > 20*minute else tick_df
    res2 = tick_df2['LastPx'].std() / tick_df2['LastPx'].mean() if tick_df2['LastPx'].mean()>0.1 else np.nan
    #
    if (res1 > 0.05) & (res2 < 0.02) & (len(tick_df)>20*(minute+1)):
        res = 1
    else :
        res = 0
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
