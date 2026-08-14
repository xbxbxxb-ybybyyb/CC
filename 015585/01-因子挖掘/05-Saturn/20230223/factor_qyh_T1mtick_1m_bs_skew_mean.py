# -*- coding: utf-8 -*-
# @Time    : 2023/02/16 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 逻辑：0930-0931,tick数据的买1-买10、卖1-卖10的偏度的均值
# score:0.02,9.4,7.1 :向卖单偏
# pj2k_931_sb_10_wish_mean
factor_name = 'qyh_T1mtick_1m_bs_skew_mean'#
def factor_qyh_T1mtick_1m_bs_skew_mean(tick_df, return_fillna_dic=False):
#     print(tick_df.name)
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 0}
    tick_df = tick_df[tick_df['MDTime'] >= 93000000]
    # list_buy =pd.DataFrame(index = tick_df['MDTime'],columns = ['skew'])
    col_list_p = ['Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price',
                  'Buy6Price', 'Buy7Price', 'Buy8Price', 'Buy9Price','Buy10Price',
                  'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price',
                  'Sell6Price', 'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price']
    col_list_v = ['Buy1OrderQty', 'Buy2OrderQty','Buy3OrderQty', 'Buy4OrderQty', 'Buy5OrderQty',
                  'Buy6OrderQty', 'Buy7OrderQty','Buy8OrderQty', 'Buy9OrderQty', 'Buy10OrderQty',
                  'Sell1OrderQty', 'Sell2OrderQty', 'Sell3OrderQty', 'Sell4OrderQty', 'Sell5OrderQty',
                  'Sell6OrderQty', 'Sell7OrderQty', 'Sell8OrderQty', 'Sell9OrderQty', 'Sell10OrderQty']
    list_buy_skew = []
    for i in tick_df['MDTime']:
        tick_df_i = tick_df[tick_df['MDTime']==i]
        array_p = tick_df_i[col_list_p].values.flatten()
        array_v = tick_df_i[col_list_v].values.flatten()
        num = np.nan_to_num(array_v).sum()
        mean = np.nan_to_num(array_p * array_v).sum() / num
        var = np.nan_to_num(((array_p - mean) ** 2) * array_v).sum() / num
        std = var ** 0.5
        skew = np.nan_to_num(((array_p - mean) ** 3) * array_v).sum() / num / (std ** 1.5)
        list_buy_skew.append(skew)
    factor_dict = {factor_name: pd.Series(list_buy_skew).mean()}
#     print(pd.Series(list_buy_skew).skew())
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
