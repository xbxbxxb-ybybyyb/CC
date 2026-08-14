# coding: utf-8
# Author：fengchi863
# Date ：2024/10/22 10:36

import pandas as pd
import numpy as np
import scipy

root_path = '/data/user/015614/Lucien/Zeus/Ceres/v1_0_4/'
bt_res_path = '/data/user/015614/Zeus/pred/Ceres/v1_0_4/config2/fsrs_s1_Xgb/'
period_list = ['period4', 'period5', 'period6', 'period7']
config = 'config2'


res_dict = dict()
for period in period_list:
    tmp = pd.read_excel(bt_res_path + f'bt_result_{period}.xlsx', index_col=0, sheet_name='test')
    res_dict[period] = tmp

corr_list = list()
for period in period_list:
    tmp = res_dict[period]
    corr = scipy.corrcoef(tmp['最大回撤'], tmp['实际参与率'])[0, 1]
    corr_list.append(corr)

print(corr_list)