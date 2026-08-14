# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
#
factor_name = 'qyh_lzttick_amt_after2zt_tmean'#
def factor_qyh_lzttick_amt_after2zt_tmean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 38237}
    p_zt = tick_df['LastPx'].max()
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    # 末次涨停时间
    time = tick_df[(tick_df['LastPx'] == p_zt)&(tick_df['LastPx_1'] != p_zt)]['MDTime'].max()
    amt_df = tick_df[tick_df['MDTime'] >= time]['TotalValueTrade']
    amt = amt_df.max() - amt_df.min()
    if len(amt_df) >0:
        amt_mean =  amt / len(amt_df)
    else:
        amt_mean = np.nan
    factor_dict = {factor_name: amt_mean}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
