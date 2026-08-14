# coding: utf-8
# Author：fengchi863
# Date ：2020/5/25 13:51

from multiprocessing import Pool

import pandas as pd

from HyperoptApi import hyperopt_wrapper
from conf.model_param_config import *
from dataApi.stockList import clean_stock_list

root_path = '/data/group/800319/junkData/IntraFactorModel/'


def get_best_model(model_type, metrics_type, stk_list, label):
    if model_type not in model_choice:
        raise Exception('Undefined model type')
    model = model_choice[model_type][0](start_date=20170103, end_date=20181231)

    def objective(params):
        print(params)
        pool = Pool(20)
        result_list = {}
        for stk in stk_list:
            para = (stk, label, params)
            result_list[stk] = pool.apply_async(model.training_methodology, (*para,))
            # model.training_methodology(stk, label, params)
        metrics_list = []
        for stk in result_list:
            try:
                metrics_list.append(result_list[stk].get()[1][metrics_type])
            except:
                model.training_methodology(stk, label, params)
        result = np.nanmean(metrics_list)
        print(params, result)
        return result

    best = hyperopt_wrapper(objective, model_choice[model_type][1], max_evals=100)
    return best


def get_single_train_result(model_type, metrics_type, stk_list, label):
    if model_type not in model_choice:
        raise Exception('Undefined model type')
    model = model_choice[model_type][0]()
    metrics_list = []
    # params = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.19, 'eval_metric': 'auc', 'lambda': 2.2,
    #           'max_depth': 32, 'n_estimators': 100.0, 'nthread': -1, 'objective': 'binary:logistic',
    #           'scale_pos_weight': 1, 'subsample': 1}

    params = {'n_estimators': 100.0, 'max_depth': 20, 'max_features': "auto",
              'class_weight': 'balanced'}
    for stk in stk_list:
        _, metrics_result = model.training_methodology(stk, label, params)
        print(stk, metrics_result[metrics_type])
        metrics_list.append(metrics_result[metrics_type])
    return np.mean(metrics_list)


pool = clean_stock_list('HS300')
isin = pool.sum(axis=0)
pool = pool[isin[isin > 0].index]

best = get_best_model('rf', 'acc', pool.columns.tolist()[:20], 'twap')
pd.to_pickle(best, root_path + 'best_hyper_params/rf.pkl')

# best = get_single_train_result('xgb', 'acc', [1], 'twap')
# pd.to_pickle(best, root_path + 'best_hyper_params/xgboost.pkl')
