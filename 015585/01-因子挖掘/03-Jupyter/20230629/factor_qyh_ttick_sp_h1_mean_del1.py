# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：前一半时间的挂卖均价对应的涨跌幅,剔除开盘后1分钟
# 全样本：0.108,58
# xly_t_tick_pqd17,66
factor_name = 'qyh_ttick_sp_h1_mean_del1'#
def factor_qyh_ttick_sp_h1_mean_del1(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0.01}
    # zcz
    dt, ticker = tick_df.index[0]
    dt = dt.strftime('%Y%m%d')
    zcz = ((ticker[0:2] == '30') & (dt >= '20200824')) | (ticker[0:2] == '68')
    #
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    tick_df = tick_df.head(int(len(tick_df)/2))
    tick_df = tick_df.iloc[20:] if len(tick_df) > 20 else tick_df
    #
    pct = tick_df['WeightedAvgOfferPx'].mean() / (tick_df['pre_close'].max()) -1
    if zcz:
        pct = pct/2
    factor_dict = {factor_name: pct}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
