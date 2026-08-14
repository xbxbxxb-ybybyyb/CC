# coding: utf-8
# Author：fengchi863
# Date ：2022/7/7 10:51

import os
import pandas as pd
from Zeus.Saturn.v1.path_conf import *

"""
#%% 王敬的模型输出样例参考
totalWjClaModelPath = '../model_eval_old/20200630~20201231_totalWjClaModel_v9.csv'
check = pd.read_csv(totalWjClaModelPath)
"""

"""
# saturns策略的所有因子和标签
saturns_path = '/data/group/800463/wangj/For_FC/data/'
file_name = 'saturns1_v5_20160101_20190930.pkl'
samples_file_path = os.path.join(saturns_path, file_name)

check = pd.read_pickle(samples_file_path)
"""

#%% 董坚存储的特征重要性
# 特征重要性，筛选因子的存储位置

saturns_path = '/data/group/800463/dongj/factor_select/saturn_s1_20220113_v2'
# file_name = 'xgb_importance_20190102_all4.xlsx'
file_name = 'xgb_importance_20190102_all4scoreconcat.xlsx'
samples_file_path = os.path.join(saturns_path, file_name)

check = pd.read_excel(samples_file_path, index_col=0)
filtered_check = check.query('corr_selected == 1')
print(check.shape, filtered_check.shape)


#%% 王总的另外一个线性筛选指标文件，可以根据文件内的指标进行筛选
# factor_path = '/data/user/013600/project2_prod/factor_bank/all_factor_20220113/factor_bank_inf_all_scene_931.xlsx'
# check = pd.read_excel(factor_path, index_col=0)
# pass

