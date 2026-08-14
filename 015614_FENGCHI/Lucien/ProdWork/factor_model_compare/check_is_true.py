# coding: utf-8
# Author：fengchi863
# Date ：2025/5/26 13:57

import os
import pandas as pd


# cmp_path = '/data/group/800463/日内强势股/p4_type1_log_parse/'
# date_list = [20241008, 20241009, 20241010, 20250401, 20250402]
date_list = [20241009]
cmp_path = '/data/group/800463/日内强势股/p4_log_parse/'
# cmp_path = '/data/group/800463/日内强势股/p4_log_parse/'
# date_list = [20250227, 20250228, 20250303, 20250304, 20250305, 20250306, 20250307, 20250310]
# date_list = [20250529]
univ = 'xdev'

#%% 因子差异对比
for _dat in date_list:
    cmp_df = pd.read_excel(cmp_path + f'因子差异/{_dat}_{univ}/Factor_diff_p4_931_{_dat}_{univ}.xlsx', sheet_name='差值大于1e-8')
    cmp_df = cmp_df.sort_values('ratio_diff', ascending=False)
    if cmp_df['ratio_diff'].iloc[0] > 1e-5:
        print(f'Error!!!!!! {_dat}_{univ}因子对比出现问题')

#%% 模型差异对比
for _dat in date_list:
    cmp_df = pd.read_excel(cmp_path + f'模型差异/{_dat}/模型差异_{_dat}_{univ}_p4_931.xlsx', sheet_name='本地投票结果')
    # cmp_df = cmp_df.query('is_sample_p4 == True & has_param == True & 是否在白名单 == 1 & 是否在黑名单 == 0')
    # cmp_df = cmp_df.query('is_sample_p4 == True & 是否在白名单 == 1 & 是否在黑名单 == 0')
    cmp_df = cmp_df.query('is_sample_p4 == True & 是否在白名单 == 1 & 是否在黑名单 == 0')
    cmp_df['check_is_false'] = cmp_df['本地投票数量'] != cmp_df[f'{univ}_sum_signals']
    if cmp_df['check_is_false'].sum() > 0:
        print(_dat)

    cmp_df = pd.read_excel(cmp_path + f'模型差异/{_dat}/模型差异_{_dat}_{univ}_p4_931.xlsx', sheet_name='差异汇总')
    assert len(cmp_df['差异汇总'].unique()) == 1
    assert cmp_df['差异汇总'].unique()[0] == "['模型不存在概率差异~~~']"

