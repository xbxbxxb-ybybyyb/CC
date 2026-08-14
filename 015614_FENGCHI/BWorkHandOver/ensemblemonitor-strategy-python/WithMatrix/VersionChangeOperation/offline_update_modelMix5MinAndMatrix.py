# @Time : 2020/12/28 19:46
# @Author : Zhichen Lu
# @File : offline_update_model.py
"""
固定20210531股票池版本

"""
import os, shutil
import pandas as pd
import numpy as np
from sklearn.externals import joblib
from ExtraTools import get_path_conf
# from online_conf import
m5_factor_path = '/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/'


def cp_factor(latest_update_date, factor_list_path, factor_map):
    if not os.path.exists(f'{local_config_path}factor_list/{latest_update_date}/'):
        os.makedirs(f'{local_config_path}factor_list/{latest_update_date}/')
    available_factor_list = pd.read_pickle(f'{local_config_path}available_factor_list.pkl')
    available_5min_factor_list = os.listdir(m5_factor_path)
    available_5min_factor_list = [x.replace('.npy', '') for x in available_5min_factor_list]
    # available_5min_factor_list = [x[0] for x in available_5min_factor_list]

    for indicator in factor_list_path:
        if os.path.exists(f'{factor_list_path[indicator]}{latest_update_date}.pkl'):
            factor_list = pd.read_pickle(f'{factor_list_path[indicator]}{latest_update_date}.pkl')
        elif os.path.exists(f'{factor_list_path[indicator]}{latest_update_date}.npy'):
            factor_list = np.load(f'{factor_list_path[indicator]}{latest_update_date}.npy').tolist()
        else:
            raise Exception(F'Factor list of {indicator} is not exist')
        if len(factor_list) != 2 and isinstance(factor_list[0], str):

            if indicator.endswith('Matrix'):
                # factor_list.update({'matrix_sw1':factor_list})
                factor_list_0 = list(map(lambda x : x[:-2],filter(lambda x : x.endswith('_0'),factor_list)))
                factor_list_1 = list(map(lambda x : x[:-2],filter(lambda x : x.endswith('_1'),factor_list)))
                factor_list = {}
                factor_list['fix'] = factor_list_0
                factor_list['matrix_sw1'] = factor_list_1
            else:
                factor_list = {'fix': factor_list}

        elif len(factor_list) == 2:
            # TODO : 替换回来
            factor_list = {'fix': factor_list[0], '5min': factor_list[1]}
            # import random
            # factor_list = {'fix':random.sample(available_factor_list,200),'5min':random.sample(available_5min_factor_list,200)}
        else:
            raise Exception('Wrong Factor List Form')

        pd.to_pickle(factor_list, f'{local_config_path}factor_list/{latest_update_date}/{indicator}_400_factor_list.pkl')

    using_fix_list, using_5min_list = set([]), set([])
    for each in factor_map:
        temp_factor_list = pd.read_pickle(factor_map[each])
        using_fix_list = using_fix_list.union(set(temp_factor_list['fix']))
        if '5min' in temp_factor_list:
            using_5min_list = using_5min_list.union(set(temp_factor_list['5min']))

    if set(using_5min_list) - set(available_5min_factor_list):
        raise Exception('存在不可使用5分钟因子')
    if set(using_fix_list) - set(available_factor_list):
        raise Exception('存在不可用FIX因子')
    pd.to_pickle(sorted(list(using_fix_list)), f'{local_config_path}using_fix_list.pkl')
    pd.to_pickle(sorted(list(using_5min_list)), f'{local_config_path}using_5min_list.pkl')


def cp_model(threshold, model_path_map, model_path, latest_update_date, factor_map):
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
            os.remove('%s/%s/%s' % (model_path, each, latest_model))
            shutil.copy(model_conf_path + latest_model, '%s/%s/%s' % (model_path, each, latest_model))

        model_validation_path = model_conf_path.replace('model_conf/', 'val_pred/')
        val_pred_list = os.listdir(model_validation_path)
        latest_val_set = list(filter(lambda x: x.startswith(str(latest_update_date)), val_pred_list))
        if len(latest_val_set) != 1:
            raise Exception('model conf are not exist or not unique')
        latest_val_set = latest_val_set[0]
        val_set[each] = pd.read_pickle(model_validation_path + latest_val_set)
        if len(val_set[each].index.levels[1])>242:
            val_set[each] = val_set[each].swaplevel(1,2)
        factor_list = pd.read_pickle(factor_map[each])
        model_conf[each] = [model_path_map[each][0], '%s/%s/%s' % (model_path, each, latest_model), factor_list]
    val_set = pd.Panel(val_set)
    val_set_sum = val_set.sum(axis=0)
    val_set_count = val_set.count(axis=0)
    subset = val_set_sum / val_set_count
    th = (subset['actual_label'] < threshold).sum() / subset.shape[0]
    pred_threshold = subset['prediction'].quantile(th)  # max(subset['prediction'].quantile(th), 0.005)
    print(pred_threshold, subset['prediction'].quantile(th))
    pd.to_pickle([model_conf, pred_threshold], local_config_path + 'model_conf/model_conf%d.pkl' % latest_update_date)


def main():
    latest_update_date = 20220429
    threshold = 0.05

    # 模型路径


    model_path_map = {
    'XGB_D': ['XGB', '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400_model_conf/'],
    'XGB_T': ['XGB', '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400_model_conf/'],
    'XGB_C': ['XGB','/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400_model_conf/'],
    'XGB_D_Matrix':['XGB','/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400_model_conf/'],
    'XGB_T_Matrix':['XGB','/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400_model_conf/'],
    'XGB_C_Matrix':['XGB','/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400_model_conf/'],

        'lightGBM_T': ['lightGBM', '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample_model_conf/'],
        'CatBoost_T': ['CatBoost', '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample_model_conf/']
    }

    factor_list_path = {
        'XGB_D': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_d_train200_test10_factor_num400_factor_list/',
        'XGB_T': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_t_train200_test10_factor_num400_factor_list/',
        'XGB_C': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelected/XGBV4FactorList_ic_c_train200_test10_factor_num400_factor_list/',
        'XGB_D_Matrix': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400_factor_list/',
        'XGB_T_Matrix': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_t_train200_test10_factor_num400_factor_list/',
        'XGB_C_Matrix': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_c_train200_test10_factor_num400_factor_list/',

        'lightGBM_T': '/data/group/800442/800319/wyl/model_record/lightgbmnew_ic_all_t_out_of_sample_train_features/',
        'CatBoost_T': '/data/group/800442/800319/wyl/model_record/catboostnew2_ic_all_t_out_sample_train_features/',
    }

    factor_map = {
        x: f'{local_config_path}factor_list/{latest_update_date}/{x}_400_factor_list.pkl' for x in ['XGB_T', 'XGB_D', 'XGB_C', 'lightGBM_T', 'CatBoost_T','XGB_D_Matrix','XGB_T_Matrix','XGB_C_Matrix']
    }
    cp_factor(latest_update_date, factor_list_path, factor_map)
    cp_model(threshold, model_path_map, model_path, latest_update_date, factor_map)


# path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')
path_conf = get_path_conf('/data/group/800319/strategy_local_path3_FixVersion0421/')

# path_conf = get_path_conf('/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/')

local_config_path, model_path = [path_conf[x] for x in ['local_config_path', 'model_path']]

main()

# sub
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

# fix_indicator,daily_indicator = 'ic_c','ic_half_c'
# f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_c_ic_half_c_model_conf/'
# os.listdir(f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/')
# target = '/data/group/800442/800319/Strong_stock/BackUp/'
# shutil.copytree(f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/',
#                 '/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/')

# import shutil
# for tag in ['d','t','c']:
#     shutil.copy(f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_{tag}_ic_half_{tag}_model_conf/20210525.json',
#                 f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_{tag}_ic_half_{tag}_model_conf/20210702.json')
#
#     shutil.copy(f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_{tag}_ic_half_{tag}_factor_list/20210525.pkl',
#                 f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_{tag}_ic_half_{tag}_factor_list/20210702.pkl')
#
#     shutil.copy(f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_{tag}_ic_half_{tag}_val_pred/20210525.pkl',
#                 f'/data/group/800442/800319/Strong_stock/BackUp/Fix5minMulti/XGBMultiFreqFix5min_train200_test10_ic_{tag}_ic_half_{tag}_val_pred/20210702.pkl')
#
# '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400_factor_list/'
# '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/CrossFix/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122/XGBV4FactorListMixCrossSWMeanOnlyShiftReSave20211122_ic_d_train200_test10_factor_num400_factor_list/20211130.pkl'