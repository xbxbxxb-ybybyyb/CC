# @Time : 2020/12/28 19:46
# @Author : Zhichen Lu
# @File : offline_update_model.py

import os, shutil
import pandas as pd
# from online_conf import local_config_path,model_path
import numpy as np
from sklearn.externals import joblib
from ExtraTools import get_path_conf

path_conf = get_path_conf('/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/')
# path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
local_config_path,model_path = [path_conf[x] for x in ['local_config_path','model_path']]

latest_update_date = 20211130
threshold = 0.05

# 模型路径
model_path_map = {
    'XGB_D': ['XGB','/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400_model_conf/'],
    'XGB_T': ['XGB', '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400_model_conf/'],
    'XGB_C': ['XGB','/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400_model_conf/'],
    'lightGBM_T':['lightGBM','/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample_model_conf/'],
    'CatBoost_T':['CatBoost','/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample_model_conf/']
}


if not os.path.exists(f'{local_config_path}factor_list/{latest_update_date}/'):
    os.mkdir(f'{local_config_path}factor_list/{latest_update_date}/')

for indicator in ['XGB_T','XGB_D','XGB_C']:
    factor_list = pd.read_pickle(model_path_map[indicator][1].replace('model_conf/','factor_list/%d.pkl'%latest_update_date))
    pd.to_pickle(factor_list,f'{local_config_path}factor_list/{latest_update_date}/{indicator}_400_factor_list.pkl')

for indicator in ['lightGBM_T','CatBoost_T']:
    factor_list = list(np.load(model_path_map[indicator][1].replace('model_conf/', 'train_features/') + '%d.npy' % latest_update_date))
    pd.to_pickle(factor_list,f'{local_config_path}factor_list/{latest_update_date}/{indicator}_400_factor_list.pkl')

factor_map = {
    x: f'{local_config_path}factor_list/{latest_update_date}/{x}_400_factor_list.pkl' for x in ['XGB_T','XGB_D','XGB_C','lightGBM_T','CatBoost_T']
    }

using_fix_list = set([])
for each in factor_map:
    temp_factor_list = pd.read_pickle(factor_map[each])
    using_fix_list = using_fix_list.union(set(temp_factor_list))
available_factor_list = pd.read_pickle(f'{local_config_path}/available_factor_list.pkl')
if set(using_fix_list) - set(available_factor_list):
    raise Exception('存在不可用因子')
pd.to_pickle(sorted(list(using_fix_list)),f'{local_config_path}using_fix_list.pkl')

model_conf = {}
val_set = {}
for each in model_path_map:
    if not os.path.exists('%s/%s/' % (model_path, each)):
        os.mkdir('%s/%s/' % (model_path, each))
    # load model
    model_conf_path = model_path_map[each][1]
    model_list = sorted(os.listdir(model_conf_path))
    latest_model = list(filter(lambda x: x.startswith(str(latest_update_date)), model_list))
    if len(latest_model) != 1:
        raise Exception('model conf are not exist or not unique')
    latest_model = latest_model[0]
    if not os.path.exists('%s/%s/%s' % (model_path, each, latest_model)):
        shutil.copy(model_conf_path + latest_model, '%s/%s/%s' % (model_path, each, latest_model))
    else:
        print(each,'exist')
        os.remove('%s/%s/%s' % (model_path, each, latest_model))
        shutil.copy(model_conf_path + latest_model, '%s/%s/%s' % (model_path, each, latest_model))

    model_validation_path = model_conf_path.replace('model_conf/', 'val_pred/')
    val_pred_list = os.listdir(model_validation_path)
    latest_val_set = list(filter(lambda x: x.startswith(str(latest_update_date)), val_pred_list))
    if len(latest_val_set) != 1:
        raise Exception('model conf are not exist or not unique')
    latest_val_set = latest_val_set[0]
    val_set[each] = pd.read_pickle(model_validation_path + latest_val_set)

    # percentile_value = (val_set['actual_label']<threshold).sum()/val_set.shape[0]
    # percentile = val_set['prediction'].quantile(percentile_value)
    # 模型类型、模型地址、使用因子类型
    factor_list = pd.read_pickle(factor_map[each])
    model_conf[each] = [model_path_map[each][0], '%s/%s/%s' % (model_path, each, latest_model), factor_list]
val_set = pd.Panel(val_set)
val_set_sum = val_set.sum(axis=0)
val_set_count = val_set.count(axis=0)
subset = val_set_sum / val_set_count
th = (subset['actual_label'] < threshold).sum() / subset.shape[0]
pred_threshold = max(subset['prediction'].quantile(th), 0.005)
print(pred_threshold,subset['prediction'].quantile(th))
pd.to_pickle([model_conf, pred_threshold], local_config_path + 'model_conf/model_conf%d.pkl' % latest_update_date)
#sub
# using_fix_list = set([])
# for date in [20201020,20201103,20201117,20201201,20201215,20201229]:
#     for indicator in ['ic_half_t','ic_half_d','ic_half_c']:
#         temp_factor_list = get_fix_factor_evaluation(400, latest_update_date, indicator)
#         using_fix_list = using_fix_list.union(set(temp_factor_list))
# lgb_factor_list = list(np.load(model_path_map['lightGBM_T'][1].replace('model_conf/','train_features/')+'%d.npy'%20210331))
# using_fix_list = using_fix_list.union(lgb_factor_list)
#
# pd.to_pickle(sorted(list(using_fix_list)),f'{local_config_path}using_fix_list.pkl')
# import shutil
# shutil.copy('/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40_model_conf/20210525.json'
# ,'/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40_model_conf/20210526.json')
#



# from online_conf import  daily_out_path
#
# summary = pd.read_pickle(f'{daily_out_path}20210802.pkl')
# for time_point in [1000,1030,1100,1300,1330,1400,1430]:
#     print((summary['signal'][time_point]<0.005).sum())



