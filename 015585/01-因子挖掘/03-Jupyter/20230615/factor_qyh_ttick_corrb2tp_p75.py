# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：末期时，挂买价格和成交均价的corr
# 快速:-0.05,30
# 全样本：
#
factor_name = 'qyh_ttick_corrb2tp_p75'#
def factor_qyh_ttick_corrb2tp_p75(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.7087}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    p75 = tick_df['LastPx'].quantile(0.75)
    tick_df = tick_df[tick_df['LastPx'] >= p75]
    corr = pd.concat([tick_df['WeightedAvgBidPx'],tick_df['ValueTrade']/
                      tick_df['VolumeTrade']],axis = 1).corr(method = 'spearman').iloc[0,1]
    factor_dict = {factor_name: corr}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
