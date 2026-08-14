# @Time : 2020/12/28 19:46
# @Author : Zhichen Lu
# @File : offline_update_model.py

import os, shutil
import pandas as pd
from online_conf import local_config_path, model_path
import numpy as np

latest_update_date = 20201229
threshold = 0.05

# 模型路径
model_path_map = {
    # 'Linear_D': ['Linear',
    #              '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LinearFactorEval_ic_all_d_train200_test10_factor_num400_norm_window_40_model_conf/'],
    # 'Linear_T': ['Linear',
    #              '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LinearFactorEval_ic_all_t_train200_test10_factor_num400_norm_window_40_model_conf/'],
    # 'Linear_C': ['Linear',
    #              '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTest/LinearFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40_model_conf/'],
    'XGB_D': ['XGB',
              '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_d_train200_test10_factor_num400_norm_window_40_model_conf/'],
    'XGB_T': ['XGB',
              '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_t_train200_test10_factor_num400_norm_window_40_model_conf/'],
    'XGB_C': ['XGB',
              '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestVRobustOpt/XGBFactorEvalYearlyParam10_ic_half_c_train200_test10_factor_num400_norm_window_40_model_conf/'],
    'lightGBM_T': ['lightGBM', '/data/group/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample_model_conf/'],
    # 'CatBoost_T':['CatBoost','/data/group/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample_model_conf/']
    # 'XGB_C': ['XGB', '/data/group/800319/Faamonitor/PL/all_mkt_ts_norm/FactorEvalOnlineTestV20210115/XGBFactorEval_ic_all_c_train200_test10_factor_num400_norm_window_40_model_conf/'],
    # 'LinearV2_D': ['LinearV2', '/data/group/800319/strategy_local_path/model/LinearV2_D/'],
    # 'LinearV2_T': ['LinearV2', '/data/group/800319/strategy_local_path/model/LinearV2_T/'],
    # 'LinearV2_C': ['LinearV2', '/data/group/800319/strategy_local_path/model/LinearV2_C/'],

}


def get_fix_factor_evaluation(num, end_index, eval_indicator):
    using_factor_list = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/available_factor_list.pkl')
    factor_evaluation = pd.read_pickle('/data/group/800319/junkData/StrongStock/external_data/ic_half.pkl')
    factor_evaluation = pd.DataFrame(factor_evaluation)
    if not eval_indicator in factor_evaluation.index.levels[0]:
        raise Exception('Unavailable indicator')
    factor_evaluation = factor_evaluation.loc[eval_indicator]
    target_date = max(list(filter(lambda x: x < end_index, factor_evaluation.index)))
    factor_evaluation = factor_evaluation.loc[target_date]
    inter_col = list(set(factor_evaluation.index).intersection(set(using_factor_list)))
    factor_list = factor_evaluation.loc[inter_col].apply(abs).sort_values(ascending=False).index.tolist()[:num]
    return sorted(factor_list)


if not os.path.exists(f'{local_config_path}factor_list/{latest_update_date}/'):
    os.mkdir(f'{local_config_path}factor_list/{latest_update_date}/')
for indicator in ['ic_half_t', 'ic_half_d', 'ic_half_c']:
    factor_list = get_fix_factor_evaluation(400, latest_update_date, indicator)
    pd.to_pickle(factor_list, f'{local_config_path}factor_list/{latest_update_date}/{indicator}_400_factor_list.pkl')

# lgb_factor_list = list(np.load(model_path_map['lightGBM_T'][1].replace('model_conf/','train_features/')+'%d.npy'%latest_update_date))
# pd.to_pickle(lgb_factor_list,f'{local_config_path}factor_list/{latest_update_date}/ic_all_t_400_factor_list_post_disease_era.pkl')

factor_map = {
    'XGB_D': f'{local_config_path}factor_list/{latest_update_date}/ic_half_d_400_factor_list.pkl',
    'XGB_T': f'{local_config_path}factor_list/{latest_update_date}/ic_half_t_400_factor_list.pkl',
    'XGB_C': f'{local_config_path}factor_list/{latest_update_date}/ic_half_c_400_factor_list.pkl',
    # 'LinearV2_D': local_config_path + 'ic_all_d_400_factor_list.pkl',
    # 'LinearV2_T': local_config_path + 'ic_all_t_400_factor_list.pkl',
    # 'LinearV2_C': local_config_path + 'ic_all_c_400_factor_list.pkl',
    'lightGBM_T': f'{local_config_path}factor_list/{latest_update_date}/ic_all_t_400_factor_list_post_disease_era.pkl',
    # 'CatBoost_T':f'{local_config_path}factor_list/{latest_update_date}/ic_all_t_400_factor_list_post_disease_era.pkl',
}

using_fix_list = set([])
for each in factor_map:
    temp_factor_list = pd.read_pickle(factor_map[each])
    using_fix_list = using_fix_list.union(set(temp_factor_list))
pd.to_pickle(sorted(list(using_fix_list)), f'{local_config_path}using_fix_list.pkl')

val_set_path = {

    # 'LinearV2_D': '/data/user/015836/HFmodel/share/20210112/LinearV2D_val_pred/',
    # 'LinearV2_T': '/data/user/015836/HFmodel/share/20210112/LinearV2T_val_pred/',
    # 'LinearV2_C': '/data/user/015836/HFmodel/share/20210112/LinearV2C_val_pred/',
}

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
        print(each, 'exist')
    # get threshold
    if each not in val_set_path:
        model_validation_path = model_conf_path.replace('model_conf/', 'val_pred/')
    else:
        model_validation_path = val_set_path[each]
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
pd.to_pickle([model_conf, pred_threshold], local_config_path + 'model_conf/model_conf%d.pkl' % latest_update_date)
