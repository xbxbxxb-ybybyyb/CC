# coding: utf-8
# Author：fengchi863
# Date ：2022/12/14 13:58

"""
针对FSV8版本因子和lowCost版本因子进行分析，对应v1025和1026版本
"""

import os
import pandas as pd
import numpy as np

group_path = '/data/group/800463/'
xgb_imptc_path = os.path.join(group_path, 'xiely/factor_select/Europa_20221024/')
xgb_imptc_fpath = os.path.join(xgb_imptc_path, 'xgb_importance_20210331_reg15_second_fac_20221116_FSV8_all_pct_graded_dropHighTimeCost.xlsx')
factor_score_path = os.path.join(group_path, 'sunss/for_xly/europa/newScore/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_xly.xlsx')

imptc_fsv8_df = pd.read_excel(xgb_imptc_fpath, index_col=0).set_index('factor_name')
imptc_lowcost_df = pd.read_excel(factor_score_fpath, index_col=0).set_index('factor_name')

filtered_imptc_fsv8_df = pd.read_excel(xgb_imptc_fpath, index_col=0).query('corr_selected==1').set_index('factor_name')
filtered_imptc_lowcost_df = pd.read_excel(factor_score_fpath, index_col=0).query('low_cost==1').set_index('factor_name')

common_col = list(set(filtered_imptc_fsv8_df.columns).intersection(set(filtered_imptc_lowcost_df.columns)))
joined_df = pd.merge(imptc_fsv8_df, imptc_lowcost_df, on='factor_name', how='outer')
joined_df['t'] = joined_df[['t_x', 't_y']].apply(lambda x: x['t_x'] if str(x['t_y']) is 'nan' else x['t_y'], axis=1)

in1_notin2 = list(set(filtered_imptc_fsv8_df.index).difference(set(filtered_imptc_lowcost_df.index)))
in2_notin1 = list(set(filtered_imptc_lowcost_df.index).difference(set(filtered_imptc_fsv8_df.index)))
in1_andin2 = list(set(filtered_imptc_lowcost_df.index).intersection(set(filtered_imptc_fsv8_df.index)))
print('in1_notin2 len:', len(in1_notin2))
print('in2_notin1 len:', len(in2_notin1))
print('in1_andin2 len:', len(in1_andin2))

print(joined_df.loc[in1_notin2].query('t == "T"').shape[0])
print(joined_df.loc[in2_notin1].query('t == "T"').shape[0])
print(joined_df.loc[in1_andin2].query('t == "T"').shape[0])

print(joined_df.loc[in1_notin2].query('t == "T-1"').shape[0])
print(joined_df.loc[in2_notin1].query('t == "T-1"').shape[0])
print(joined_df.loc[in1_andin2].query('t == "T-1"').shape[0])

print(filtered_imptc_fsv8_df.shape[0])
print(filtered_imptc_fsv8_df.query('t == "T"').shape[0])
print(filtered_imptc_fsv8_df.query('t == "T-1"').shape[0])
print(filtered_imptc_lowcost_df.shape[0])
print(filtered_imptc_lowcost_df.query('t == "T"').shape[0])
print(filtered_imptc_lowcost_df.query('t == "T-1"').shape[0])

check = filtered_imptc_fsv8_df.loc[in1_notin2]
check = check.sort_values('count', ascending=True)

"""
配合v1_0_29测试
"""
from LucienUtil.FileUtil import FileUtil
from Zeus.Europa.v1_0_29.path_conf import factor_path
FileUtil.save_list2pkl(in1_notin2, factor_path, 'middle_cost_23.pkl')