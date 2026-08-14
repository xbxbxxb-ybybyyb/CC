# -*- coding: utf-8 -*-
# @Time    : 2023/02/23 14:06
# @Author  : qinyuhao

import numpy as np
import pandas as pd
# 待提交
# 逻辑：平均开板时长
# score:11,-0.07
# jpt_label_pattern:9,0.06
# lzt_day_pattern:8,0.06
# lzt_label_pattern:8,0.06
# Lzt_pre_post_ZT_std_prod:10,-0.07
factor_name = 'qyh_lzttick_t_notzt_mean'#
def factor_qyh_lzttick_t_notzt_mean(tick_df, return_fillna_dic=False):
    if return_fillna_dic:
        # 返回因子为nan时的填充值
        return {factor_name: 7.5}
    p_zt = tick_df['LastPx'].max()
    tick_df['LastPx_1'] = tick_df['LastPx'].shift(1)# 前一个tick的价格
    time = tick_df[tick_df['LastPx'] == p_zt]['MDTime'].min()# 首次封板时间
    tick_df = tick_df[tick_df['MDTime'] >= time]
    length = len(tick_df[tick_df['LastPx']<p_zt])
    # 开板次数
    length_2 = len(tick_df[(tick_df['LastPx'] == p_zt) & (tick_df['LastPx_1'] < p_zt)]) - 1
    #
    if length_2 >0:
        ratio = 3 * length / length_2
    else:
        ratio = 0
    factor_dict = {factor_name: ratio}
    # ---------------------------------------------------------------------------------------------------------------
    return pd.Series(factor_dict)

    # 格式上需要注意的部分：
    # 1.因子文件代码名称为'factor_因子名称.py';
    # 2.函数名称为'factor_因子名称()';
    # 3.在return_fillna_dic中返回的dict的key为因子名称;
    # 4.在返回的factor_dic中key也为因子名称;
    # 5以上的四个因子名称应该统一。
