# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：0920-0925,买1额的标准差
# score:0.05,10.5,6 :集合竞价时，成交额波动大，
# 无
factor_name = 'qyh_T1mtick_call_amt_std_5'#
def factor_qyh_T1mtick_call_amt_std_5(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5}
    tick_df = tick_df[tick_df['MDTime'] >= 92000000]
    tick_df = tick_df[tick_df['TradingPhaseCode'] == '1']
    amt = tick_df['Buy1Price'] * tick_df['Buy1OrderQty']
    if abs(amt.mean()) > 1:
        std = amt.std() / amt.mean()
    else:
        std = np.nan
    #
    factor_dict = {factor_name: std}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
