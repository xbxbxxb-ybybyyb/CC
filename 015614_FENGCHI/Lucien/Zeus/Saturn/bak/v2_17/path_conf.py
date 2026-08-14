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

#%% 20220819 filter v6.3样本（加入93030时因子）
saturn_data_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_3/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_scene_V6_3_20160101_20201231.pkl')
saturn_data_fit_fpath = os.path.join(saturn_data_path, 'factor_df_all_scene_V6_3_20160101_20201231.pkl')

filter_factor_path = os.path.join(group_path, 'xiely/factor_select/Saturn_v6/')
filter_factor_fpath = os.path.join(filter_factor_path, 'xgb_importance_20190102_allreg4_v6.3_3period.xlsx')

factor_score_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_3/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_scene_V6_3.xlsx')

#%% 回测输出根路径
bt_out_path = os.path.join(fc_path, 'Zeus/backtest/')
pred_out_path = os.path.join(fc_path, 'Zeus/pred/')
log_path = os.path.join(fc_path, 'Zeus/logs/')
factor_path = os.path.join(fc_path, 'Zeus/factor_list/')
multi_path = os.path.join(fc_path, 'Zeus/multi_result/')    # 保存回测结果
factor_select_path = os.path.join(fc_path, 'Zeus/factor_select_path/')  # 保存因子筛选的路径

junk_path = os.path.join(fc_path, 'junkData/')