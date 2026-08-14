# coding: utf-8
# Author：fengchi863

"""
Saturn全样本训练任务
"""

import os

#%% 根目录们
group_path = '/data/group/800463/'
fc_group_path = os.path.join(group_path, 'fengc/')
fc_path = '/data/user/015614/'
wwd_path = '/data/user/013600/'

#%% V6_20220927
saturn_data_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_20220927/V6_20220927_933_3period/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_933_20160101_20201231.pkl')
saturn_data_fit_fpath = os.path.join(saturn_data_path, 'factor_df_all_933_20160101_20201231.pkl')

filter_factor_path = os.path.join(group_path, 'xiely/factor_select/Saturn_v6/')
filter_factor_fpath = os.path.join(filter_factor_path, 'xgb_importance_20190102_reg15_second_all_V6_20220927_933_FSV9_v2o10d3_new_3period.xlsx')

factor_score_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_20220927/V6_20220927_933_3period/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_933_emotion.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
multi_path = os.path.join(fc_path, 'Zeus/multi_result/')    # 保存回测结果
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select_path/')  # 保存因子筛选的路径

junk_path = os.path.join(fc_path, 'junkData/')