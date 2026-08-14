# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：0931，价格下降时，vwap / price
# score:4,-0.04
# 无
factor_name = 'qyh_T1mtick_1m_p_vwap2p_down'#
def factor_qyh_T1mtick_1m_p_vwap2p_down(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.001}

    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['delta_lastpxpre'] = tick_df['LastPx'] - tick_df['LastPx'].shift(1)
    tick_df = tick_df[tick_df['delta_lastpxpre'] <0]
    vwap2p =((tick_df['amt'] / tick_df['vol']) / tick_df['LastPx']).mean()
    factor_dict = {factor_name: vwap2p}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
