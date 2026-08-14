# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：下跌时，买1-买均对应收益率的均值的差
# 快速：44,0.09
# 全样本：55,0.1
# sss_tk_bpctdiff_all_mean:48
factor_name = 'qyh_ttick_b12b_d_mean'#
def factor_qyh_ttick_b12b_d_mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.036}
    tick_df = tick_df[tick_df['MDTime'] > 93000000]
    tick_df['ValueTrade'] = tick_df['TotalValueTrade'] - tick_df['TotalValueTrade'].shift(1).fillna(0)
    tick_df['VolumeTrade'] = tick_df['TotalVolumeTrade'] - tick_df['TotalVolumeTrade'].shift(1).fillna(0)
    #
    tick_df['tradep'] = tick_df['ValueTrade'] / tick_df['VolumeTrade']
    tick_df2 =tick_df[tick_df['tradep'] < tick_df['tradep'].shift(1)]
    #
    if tick_df2.empty:
        pct2 = np.nan
    else:
        pct2 =  ((tick_df2['Buy1Price'] - tick_df2['WeightedAvgBidPx']) / (tick_df2['pre_close'].max())).mean()
    #
    # pct = pct1 - pct2
    factor_dict = {factor_name: pct2}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
