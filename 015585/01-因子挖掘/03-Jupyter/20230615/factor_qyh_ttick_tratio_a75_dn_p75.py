# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：成交活跃且下跌的低价时间占比
# 快速:0.02,2
# 全样本：
#
factor_name = 'qyh_ttick_tratio_a75_dn_p75'#
def factor_qyh_ttick_tratio_a75_dn_p75(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.4}
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    p = tick_df['LastPx'].quantile(0.75)
    length = len(tick_df)
    #
    limit = tick_df['ValueTrade'].quantile(0.75)
    tick_df = tick_df[tick_df['ValueTrade'] >= limit]
    #
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df = tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    #
    tick_df = tick_df[tick_df['LastPx'] <= p]
    ratio = len(tick_df) / length if length > 0 else np.nan
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
