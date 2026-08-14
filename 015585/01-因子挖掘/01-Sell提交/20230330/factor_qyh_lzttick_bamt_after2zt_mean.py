# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
factor_name = 'qyh_lzttick_bamt_after2zt_mean'#
def factor_qyh_lzttick_bamt_after2zt_mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 47400518}
    p_zt = tick_df['LastPx'].max()
    tick_df = tick_df[tick_df['MDTime'] < 145700000]
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    # 末次涨停时间
    time_1 = tick_df[(tick_df['LastPx'] == p_zt)&(tick_df['LastPx_1'] != p_zt)]['MDTime'].max()
    tick_df = tick_df[tick_df['MDTime'] >= time_1]
    #
    col_list_p = ['Buy1Price', 'Buy2Price', 'Buy3Price', 'Buy4Price', 'Buy5Price',
                  'Buy6Price', 'Buy7Price', 'Buy8Price', 'Buy9Price','Buy10Price',
                  'Sell1Price', 'Sell2Price', 'Sell3Price', 'Sell4Price', 'Sell5Price',
                  'Sell6Price', 'Sell7Price', 'Sell8Price', 'Sell9Price', 'Sell10Price']
    col_list_v = ['Buy1OrderQty', 'Buy2OrderQty','Buy3OrderQty', 'Buy4OrderQty', 'Buy5OrderQty',
                  'Buy6OrderQty', 'Buy7OrderQty','Buy8OrderQty', 'Buy9OrderQty', 'Buy10OrderQty',
                  'Sell1OrderQty', 'Sell2OrderQty', 'Sell3OrderQty', 'Sell4OrderQty', 'Sell5OrderQty',
                  'Sell6OrderQty', 'Sell7OrderQty', 'Sell8OrderQty', 'Sell9OrderQty', 'Sell10OrderQty']
    for i in range(20):
        if i <= 9:
            tick_df['buyamt'+str(i)] = tick_df[col_list_p[i]] * tick_df[col_list_v[i]]
            if i == 0:
                tick_df['buytotal'] = tick_df['buyamt'+str(i)]
            else:
                tick_df['buytotal'] = tick_df['buytotal'] + tick_df['buyamt'+str(i)]
        # if i == 9:
        #     tick_df['bstotal'] = tick_df['buytotal']
        # if i > 9:
        #     tick_df['sellamt'+str(i)] = tick_df[col_list_p[i]] * tick_df[col_list_v[i]]
        #     tick_df['bstotal'] = tick_df['bstotal'] + tick_df['sellamt'+str(i)]
    amt = tick_df['buytotal'].mean()
    factor_dict = {factor_name: amt}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
