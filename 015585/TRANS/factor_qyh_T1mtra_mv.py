# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：市值
# score:0.03 不好，月度corr = 0
#
factor_name = 'qyh_T1mtra_mv'#concenteration
def factor_qyh_T1mtra_mv(transaction_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.5}
    transaction_df = transaction_df[transaction_df['TradePrice'] > 0]
    mv = transaction_df['pre_close'][0] * transaction_df['ff_shares'][0]

    factor_dict = {factor_name: mv}

    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
