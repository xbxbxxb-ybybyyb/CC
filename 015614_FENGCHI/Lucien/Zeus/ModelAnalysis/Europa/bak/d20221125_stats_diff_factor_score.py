# coding: utf-8
# Author：fengchi863
# Date ：2022/11/25 14:05

import pandas as pd

new_root_path = '/data/group/800463/sunss/for_xly/europa/20221116/'
new_score_fname = new_root_path + 'factor_bank_inf_all.xlsx'

old_root_path = '/data/group/800463/sunss/for_xly/europa/old/'
old_score_fname = old_root_path + 'factor_bank_inf_v1.xlsx'

new_factor_score = pd.read_excel(new_score_fname, index_col=0)
old_factor_score = pd.read_excel(old_score_fname, index_col=0)

new_factor_list = new_factor_score.dropna(subset=['t'])['factor_name'].tolist()
old_factor_list = old_factor_score.dropna(subset=['in_score_value'])['factor_name'].tolist()
common_factor_list = list(set(new_factor_list).intersection(set(old_factor_list)))
print(len(new_factor_list), len(old_factor_list), len(common_factor_list))

new_check = new_factor_score.set_index('factor_name').loc[common_factor_list]
old_check = old_factor_score.set_index('factor_name').loc[common_factor_list]

watch_col = ['区间1-out-value', '区间2-out-value', '区间3-out-value']
res_df = pd.DataFrame(index=common_factor_list, columns=watch_col)
old_check = old_check.rename({
    'all_score_value': '区间1-out-value',
    'long_score_value': '区间2-out-value',
    'longlong_score_value': '区间3-out-value'
}, axis=1)
for _watch in watch_col:
    diff = new_check[_watch] - old_check[_watch]
    res_df.loc[common_factor_list, _watch] = diff
check1 = (res_df < 0).sum(axis=0) / len(res_df)
check2 = res_df.sum(axis=0)