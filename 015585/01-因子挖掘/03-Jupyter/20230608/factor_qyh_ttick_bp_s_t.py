# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# dtj
# 逻辑：挂买均价对应的涨跌幅在拉升前的值
# 快速:0.05，21
# 全样本：0.06，39
#
factor_name = 'qyh_ttick_bp_s_t'#
def factor_qyh_ttick_bp_s_t(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.98}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df2 = tick_df[tick_df['LastPx'] <= tick_df['LastPx'].quantile(0.25)]
    pct2 = (tick_df2['WeightedAvgBidPx'] / (tick_df['pre_close'].max())).tail(1).mean()
    factor_dict = {factor_name: pct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
