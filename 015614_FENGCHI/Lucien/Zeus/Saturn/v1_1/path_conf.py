# coding: utf-8
# Author：fengchi863

import os

root_path = '/data/group/800463/'
user_path = '/data/user/015614/'
wwd_path = '/data/user/013600/'

#%% Saturn路径
# saturn_data_path = os.path.join(root_path, 'wangj/For_FC/data/saturns1_v5_20160101_20190930.pkl')
# filter_factor_path = os.path.join(root_path, 'dongj/factor_select/saturn_s1_20220113_v2/')
# filter_factor_file_path = os.path.join(filter_factor_path, 'xgb_importance_20190102_all4scoreconcat.xlsx')

saturn_data_path = os.path.join(wwd_path, 'project2_prod/factor_bank/all_factor_20220712/filter_v1_1/')
saturn_data_fpath = os.path.join(saturn_data_path, 'factor_df_filter_v1_1_931_20160101_20200630.pkl')

filter_factor_path = os.path.join(root_path, 'xiely/factor_select/Saturn_v6/')
filter_factor_fpath = os.path.join(filter_factor_path, 'xgb_importance_20190102_allcla4_v6.xlsx')

factor_score_path = os.path.join(wwd_path, 'project2_prod/factor_bank/all_factor_20220712/filter_v1_1/')
factor_score_fpath = os.path.join(factor_score_path, 'factor_bank_inf_filter_v1_1_931.xlsx')
