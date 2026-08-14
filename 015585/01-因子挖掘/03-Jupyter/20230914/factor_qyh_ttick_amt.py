# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# T日成交额
#
#
factor_name = 'qyh_ttick_amt'#
def factor_qyh_ttick_amt(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: np.nan}
    #
    # tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    res = tick_df['TotalValueTrade'].max()
    pre = tick_df['pre_close'].values[0]
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    if len(tick_df) > 100:
        tick_df = tick_df.tail(100)
        if (tick_df['LastPx'].max() - tick_df['LastPx'].min())/pre < 0.05:
            res = np.nan
    else:
        if len(tick_df) < 60:
            res = np.nan
        elif (tick_df['LastPx'].max() - tick_df['LastPx'].min())/pre < 0.05:
            res = np.nan
    #
    factor_dict = {factor_name: res}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
