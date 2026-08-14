 # -*- coding: utf-8 -*-
# @Time    : 2023/05/18 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
# 逻辑：昨日涨停票，目前的tick的日内涨跌幅均值
# 快速：33,0.051
# 全样本：23,0.052
#
factor_name = 'qyh_emo_pct_in_all'#
def factor_qyh_emo_pct_in_all(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['close_zt'] == True]
    tick_df = tick_df[tick_df['MDTime'] >= 92500000]
    tick_df = tick_df[tick_df['Buy1Price'] > 1]
    tick_df = tick_df.groupby(['dt','Ticker']).nth([0,-1])

    p_delta = tick_df.groupby(['dt', 'Ticker'])['Buy1Price'].apply(lambda x: x.tail(1).mean() - x.head(1).mean())
    tick_df = tick_df.groupby(['dt', 'Ticker']).nth([-1])
    tick_df['pct'] = tick_df['Buy1Price'] / tick_df['pre_close'] - 1
    tick_df['in_pct'] = p_delta / tick_df['pre_close']
    # tick_df['in_pct'] = tick_df.apply(lambda x: x['in_pct'] + 0.05 if x['pct'] > 0.095 else x['in_pct'], axis=1)
    factor_dict = {factor_name: tick_df['in_pct'].mean()}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
