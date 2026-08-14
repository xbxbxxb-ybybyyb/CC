# coding: utf-8
# Author：fengchi863
# Date ：2022/10/11 13:43

import pandas as pd
from LucienUtil.FileUtil import FileUtil
from Zeus.Saturn.v3_0_15.path_conf import factor_path
from Zeus.Saturn.v3_0_25.path_conf import filter_factor_fpath, factor_score_fpath

factor_list0 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_21/', 'factor_list.pkl')
factor_list1 = FileUtil.read_list(factor_path + f'SaturnS1/lgb_reg_model/v3_0_25/', 'factor_list.pkl')

print(len(factor_list0))
print(len(factor_list1))

in_list1_not_list0 = list(set(factor_list1).difference(set(factor_list0)))
in_list0_not_list1 = list(set(factor_list0).difference(set(factor_list1)))
print(f'list1中不同于list0的因子个数有{len(in_list1_not_list0)}个')
print(f'list0中不同于list1的因子个数有{len(in_list0_not_list1)}个')


filter_factor = pd.read_excel(filter_factor_fpath, index_col=0)

diff_filter_factor = filter_factor.set_index('factor_name').loc[in_list1_not_list0]
used_filter_factor = filter_factor.set_index('factor_name').loc[factor_list1]
new_emotion_factor = filter_factor.query('factor_owner == "emotion"')

sss_change_factor_fpath = '/data/group/800463/sunss/for_xly/saturn/V6_20220927/v20220927因子变动列表.xlsx'
sss_change_factor = pd.read_excel(sss_change_factor_fpath)['Unnamed: 1'].dropna().tolist()
list(set(diff_filter_factor.index.tolist()).intersection(set(sss_change_factor)))

factor_score = pd.read_excel(factor_score_fpath).set_index('factor_name')
tmp = pd.merge(diff_filter_factor, factor_score, on='factor_name')
