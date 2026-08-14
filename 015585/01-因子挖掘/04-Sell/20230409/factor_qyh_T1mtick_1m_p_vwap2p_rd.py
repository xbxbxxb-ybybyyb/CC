# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：0931，价格上升时，vwap / price - 下降时vwap / price
# -0.026,2
# wu
factor_name = 'qyh_T1mtick_1m_p_vwap2p_rd'#
def factor_qyh_T1mtick_1m_p_vwap2p_rd(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.001}

    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['delta_lastpxpre'] = tick_df['LastPx'] - tick_df['LastPx'].shift(1)
    # raise
    tick_df_1 = tick_df[tick_df['delta_lastpxpre'] >0]
    vwap2p_r =((tick_df_1['amt'] / tick_df_1['vol']) / tick_df_1['LastPx']).mean()
    # down
    tick_df_2 = tick_df[tick_df['delta_lastpxpre'] <0]
    vwap2p_d =((tick_df_2['amt'] / tick_df_2['vol']) / tick_df_2['LastPx']).mean()
    factor_dict = {factor_name: vwap2p_r - vwap2p_d}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
