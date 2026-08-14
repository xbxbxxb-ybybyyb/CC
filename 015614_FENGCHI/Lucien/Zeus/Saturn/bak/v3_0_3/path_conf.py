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

#%% Saturn路径
# saturn_data_path = os.path.join(root_path, 'wangj/For_FC/data/saturns1_v5_20160101_20190930.pkl')
# filter_factor_path = os.path.join(root_path, 'dongj/factor_select/saturn_s1_20220113_v2/')
# filter_factor_file_path = os.path.join(filter_factor_path, 'xgb_importance_20190102_all4scoreconcat.xlsx')

#%% 20220712 修改后的路径
# saturn_data_path = os.path.join(wwd_path, 'project2_prod/factor_bank/all_factor_20220113/')
# saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_scene_931_20160101_20201231.pkl')
# saturn_data_fit_fpath = os.path.join(saturn_data_path, 'factor_df_all_scene_931_20160101_20201231.pkl')
#
# filter_factor_path = os.path.join(group_path, 'xiely/factor_select/Saturn_v5/')
# filter_factor_fpath = os.path.join(filter_factor_path, 'xgb_importance_20190102_all4_v5.xlsx')
#
# factor_score_path = os.path.join(wwd_path, 'project2_prod/factor_bank/all_factor_20220113/')
# factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_all_scene_931.xlsx')

# 加入93030后的因子的样本v6.1
saturn_data_path = os.path.join(group_path, 'sunss/for_xly/saturn/V6_3/')
saturn_data_test_fpath = os.path.join(saturn_data_path, 'factor_df_all_scene_V6_3_20160101_20201231.pkl')
saturn_data_fit_fpath = os.path.join(saturn_data_path, 'factor_df_all_scene_V6_3_20160101_20201231.pkl')

filter_factor_path = os.path.join(group_path, 'xiely/factor_select/Saturn_v6/')
filter_factor_fpath = os.path.join(filter_factor_path, 'xgb_importance_20190102_allreg4_V6.3_3period_v3.xlsx')

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