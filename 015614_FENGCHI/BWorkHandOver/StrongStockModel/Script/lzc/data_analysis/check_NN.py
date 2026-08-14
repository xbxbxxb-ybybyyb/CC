# @Time : 2020/11/3 19:43
# @Author : Zhichen Lu
# @File : check_NN.py
import pandas as pd
import os
from sklearn import metrics
# from conf.path_config import root_path

path = '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/NN_param_optimization/'
file_list = os.listdir(path)
file_list = sorted(list(filter(lambda x :x.endswith('.pkl'),file_list)))
corr_series=pd.Series()
mae_series = pd.Series()
for each in file_list:
    check = pd.read_pickle(path+each)
    corr_series[each.split('_')[0]] = check.corr().values[0,1]
    mae_series[each.split('_')[0]] = metrics.mean_absolute_error(check['actual_label'],check['prediction'])
for each in ['XGB_train200_test10_factor_num400_norm_window_40.pkl','NNRedefineCorrOnly_train200_test10_factor_num400_norm_window_40.pkl']:

    base_line_label = pd.read_pickle('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/reg_norm_window_compare/'+each)
    base_line_label = base_line_label.loc[:20151113]
    corr_series[each.split('_')[0]] = base_line_label.corr().values[0,1]
    mae_series[each.split('_')[0]] = metrics.mean_absolute_error(base_line_label['actual_label'],base_line_label['prediction'])

res = pd.DataFrame({'corr':corr_series,'mae':mae_series})