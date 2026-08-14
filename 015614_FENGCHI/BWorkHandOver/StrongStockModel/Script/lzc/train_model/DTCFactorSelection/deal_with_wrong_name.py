# @Time : 2020/11/25 14:57
# @Author : Zhichen Lu
# @File : deal_with_wrong_name.py
import pandas as pd
import os,shutil

indicator = 'ic_all_d'
source_dir = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_%s_train200_test10_factor_num400_norm_window_40_val_pred/'%indicator
destination_dir = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_%s_train200_test10_factor_num400_norm_window_40_val_pred/'%indicator
base_dir = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_%s_train200_test10_factor_num400_norm_window_40_model_conf/'%indicator

if not os.path.exists(destination_dir):
    os.mkdir(destination_dir)
date_list = os.listdir(base_dir)
for each in date_list:
    shutil.copy(source_dir+each,destination_dir+each)
    os.remove(source_dir+each)
    print(each)
#
# shutil.copy('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl',
#             '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40.pkl')
# shutil.copy('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl',
#             '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40.pkl')
# shutil.copy('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl',
#             '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEval/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40.pkl')