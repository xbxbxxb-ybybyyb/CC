# coding: utf-8
# Author：fengchi863

"""
Europa全样本训练任务
"""

import os

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'

saturn_data_path = os.path.join(group_path, 'sunss/for_xly/europa/20221116/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_20160101_20211231.pkl')
saturn_data_fit_fpath = os.path.join(saturn_data_path, 'factor_df_all_20160101_20211231.pkl')

filter_factor_path = os.path.join(group_path, 'sunss/for_xly/europa/20221116/')
filter_factor_fpath = os.path.join(filter_factor_path, 'regression_select_result_20160101_20190930.xlsx')

factor_score_path = os.path.join(group_path, 'sunss/for_xly/europa/20221116/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
multi_path = os.path.join(fc_path, 'Zeus/multi_result/')    # 保存回测结果
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select_path/')  # 保存因子筛选的路径

junk_path = os.path.join(fc_path, 'junkData/')