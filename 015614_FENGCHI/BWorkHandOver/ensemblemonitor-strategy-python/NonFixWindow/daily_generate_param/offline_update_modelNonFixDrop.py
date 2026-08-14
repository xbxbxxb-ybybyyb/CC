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

non_fix_path = '/data/group/800319/strategy_local_path_nonfix/'
# non_fix_path = '/data/group/800319/strategy_local_path3/'
non_fix_model_path = f'{non_fix_path}model/'
non_fix_model_conf_path = f'{non_fix_path}model_conf/'

m5_factor_path = '/arch1/group/800442/800319/MinFactorSuper/FactorFixData/Factor/'


def cp_factor(latest_update_date, factor_list_path, factor_map):
    if not os.path.exists(f'{non_fix_path}factor_list/{latest_update_date}/'):
        os.makedirs(f'{non_fix_path}factor_list/{latest_update_date}/')
    available_factor_list = pd.read_pickle(f'{non_fix_path}available_factor_list.pkl')
    available_5min_factor_list = os.listdir(m5_factor_path)
    available_5min_factor_list = [x.replace('.npy', '') for x in available_5min_factor_list]
    using_fix_list, using_5min_list = set([]), set([])

    for indicator in factor_list_path:
        if os.path.exists(f'{factor_list_path[indicator]}{latest_update_date}.pkl'):
            factor_list = pd.read_pickle(f'{factor_list_path[indicator]}{latest_update_date}.pkl')
        elif os.path.exists(f'{factor_list_path[indicator]}{latest_update_date}.npy'):
            factor_list = np.load(f'{factor_list_path[indicator]}{latest_update_date}.npy').tolist()
        else:
            raise Exception(F'Factor list of {indicator} is not exist')
        if len(factor_list) != 2 and isinstance(factor_list[0], str):

            if indicator.endswith('Matrix'):
                factor_list_0 = list(map(lambda x : x[:-2],filter(lambda x : x.endswith('_0'),factor_list)))
                factor_list_1 = list(map(lambda x : x[:-2],filter(lambda x : x.endswith('_1'),factor_list)))
                factor_list = {}
                factor_list['fix'] = factor_list_0
                factor_list['matrix_sw1'] = factor_list_1
            else:
                factor_list = {'fix': factor_list}

        elif len(factor_list) == 2:
            factor_list = {'fix': factor_list[0], '5min': factor_list[1]}
        else:
            raise Exception('Wrong Factor List Form')
        if not os.path.exists(os.path.split(factor_map[indicator])[0]):
            os.makedirs(os.path.split(factor_map[indicator])[0])
        pd.to_pickle(factor_list, factor_map[indicator])

    # for each in factor_map:
    #     temp_factor_list = factor_list#pd.read_pickle(factor_map[each])
        using_fix_list = using_fix_list.union(set(factor_list['fix']))
        if '5min' in factor_list:
            using_5min_list = using_5min_list.union(set(factor_list['5min']))

    if set(using_5min_list) - set(available_5min_factor_list):
        raise Exception('存在不可使用5分钟因子')
    if set(using_fix_list) - set(available_factor_list):
        raise Exception('存在不可用FIX因子')
    # pd.to_pickle(sorted(list(using_fix_list)), f'{non_fix_path}using_fix_list.pkl')
    # pd.to_pickle(sorted(list(using_5min_list)), f'{non_fix_path}using_5min_list.pkl')
    return using_fix_list,using_5min_list

def cp_model(threshold,short_threshold, model_path_map, model_path, latest_update_date, factor_map,bar):
    model_conf = {}
    val_set = {}
    for each in model_path_map:
        if not os.path.exists('%s/%s/' % (model_path, each)):
            os.makedirs('%s/%s/' % (model_path, each))
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
    if bar==8:
        th = (subset['actual_label'] < threshold).sum() / subset.shape[0]
    else:
        th = (subset['1_day_label'] < threshold).sum() / subset.shape[0]
    pred_threshold = subset['prediction'].quantile(th)  # max(subset['prediction'].quantile(th), 0.005)
    print(pred_threshold, subset['prediction'].quantile(th))

    th_short =(subset['actual_label'] < short_threshold).sum() / subset.shape[0]
    short_pred_threshold = subset['prediction'].quantile(th_short)


    pd.to_pickle({'model_conf':model_conf, 'long_threshold':pred_threshold,'short_threshold':short_pred_threshold}, f'{non_fix_model_conf_path}/{latest_update_date}/Future_{bar}_bar.pkl' )


def main(bar,latest_update_date,threshold = 0.05,short_threshold=0):

    if not os.path.exists(f'{non_fix_model_conf_path}/{latest_update_date}/'):
        os.makedirs(f'{non_fix_model_conf_path}/{latest_update_date}/')
    model_path_map = {
    'XGB_D': ['XGB', f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400_model_conf/'],
    'XGB_T': ['XGB', f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400_model_conf/'],
    'XGB_C': ['XGB', f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400_model_conf/'],

    'XGB_D_Matrix':['XGB',f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/SWMeanFuture_{bar}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400_model_conf/'],
    'XGB_T_Matrix':['XGB',f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/SWMeanFuture_{bar}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400_model_conf/'],
    'XGB_C_Matrix':['XGB',f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/SWMeanFuture_{bar}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400_model_conf/'],
        'LightGBM_T': ['lightGBM',f'/data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/lightgbm_all_sample_ic_all_t_model_conf/'],
        'CatBoost_T': ['CatBoost',f'/data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/catboost_all_sample_ic_all_t_model_conf/'],

    }

    factor_list_path = {
        'XGB_D': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_d_train200_test10_factor_num400_factor_list/',
        'XGB_T': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_t_train200_test10_factor_num400_factor_list/',
        'XGB_C': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/Future_{bar}_bar/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400/XGBV4ReversalResReselect_ic_c_train200_test10_factor_num400_factor_list/',
        'XGB_D_Matrix': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/SWMeanFuture_{bar}_bar/XGB_SWMean_ic_d_train200_test10_factor_num400/XGB_SWMean_ic_d_train200_test10_factor_num400_factor_list/',
        'XGB_T_Matrix': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/SWMeanFuture_{bar}_bar/XGB_SWMean_ic_t_train200_test10_factor_num400/XGB_SWMean_ic_t_train200_test10_factor_num400_factor_list/',
        'XGB_C_Matrix': f'/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/MonthlySelectedMDDImproveV8BarWith1DayLabel_20220322_keep5DropProbFactor/SWMeanFuture_{bar}_bar/XGB_SWMean_ic_c_train200_test10_factor_num400/XGB_SWMean_ic_c_train200_test10_factor_num400_factor_list/',
        'LightGBM_T':f'/data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/lightgbm_all_sample_ic_all_t_train_features/',
        'CatBoost_T':f'/data/group/800442/800319/wyl/model_record/nonfix/future_{bar}_bar/catboost_all_sample_ic_all_t_train_features/',

    }

    factor_map = {
        x: f'{non_fix_model_path}factor_list/{latest_update_date}/Future_{bar}_bar/{x}_400_factor_list.pkl' for x in ['XGB_T', 'XGB_D', 'XGB_C','XGB_D_Matrix','XGB_T_Matrix','XGB_C_Matrix','LightGBM_T','CatBoost_T']
    }


    model_path = f'{non_fix_model_path}/Future_{bar}_bar/'
    u_fix_list,u_5min_list = cp_factor(latest_update_date, factor_list_path, factor_map)
    cp_model(threshold,short_threshold, model_path_map, model_path, latest_update_date, factor_map,bar)
    return u_fix_list,u_5min_list


# path_conf = get_path_conf('/data/group/800319/strategy_local_path3/')


# path_conf = get_path_conf('/data/group/800442/800319/EMExternalPoolTrace/strategy_local_path_TX/')
if __name__ == '__main__':
    fix_list,m5_list = set([]),set([])
    latest_update_date = 20220330
    for b in range(1,9):
        u_fix_list,u_5min_list = main(b,latest_update_date=latest_update_date,threshold=0.05,short_threshold=0)
        fix_list = fix_list.union(set(u_fix_list))
        m5_list = m5_list.union(set(u_5min_list))
    pd.to_pickle(sorted(list(fix_list)),f'{non_fix_model_conf_path}/{latest_update_date}/using_fix_list.pkl')
    pd.to_pickle(sorted(list(fix_list)),f'{non_fix_path}/using_fix_list.pkl')
    pd.to_pickle(sorted(list(m5_list)),f'{non_fix_model_conf_path}/{latest_update_date}/using_5min_list.pkl')

    # check = pd.read_pickle('/data/group/800442/800319/junkData/StrongStock//external_data/problem_factor/20220304.pkl')
    # set(fix_list).intersection(check)




