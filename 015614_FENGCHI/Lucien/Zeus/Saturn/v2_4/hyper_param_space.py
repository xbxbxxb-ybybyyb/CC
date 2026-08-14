# coding: utf-8
# Author：fengchi863

from hyperopt import hp
import numpy as np
from decimal import Decimal

def gen_arith_sequ(start, end, interval):
    gen_list = list()
    val = start
    while val <= end:
        gen_list.append(val)
        val += interval
    return gen_list

# 初版，尚未调参：9.28 4686w | 这个是在错误的标签上回测的结果
xgb_clf_param0 = {'booster': 'gbtree', 'colsample_bytree': 1, 'factor_num': 200, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 2000.0, 'len_train': 4000.0, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'pct_threshold': 0.040962046550346534, 'random_state': 2022, 'refer_num': 400.0, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'seed': 2022, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}
# 提交版本
xgb_clf_param1111 = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'factor_num': 160.0, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 1500.0, 'len_train': 5000.0, 'max_depth': 4, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'objective': 'binary:logistic', 'pct_threshold': 0.04824361775850608, 'random_state': 2022, 'refer_num': 2000.0, 'reg_alpha': 0, 'reg_lambda': 1, 'scale_pos_weight': 3, 'seed': 2022, 'silent': True, 'subsample': 1.0, 'tree_method': 'gpu_hist'}
xgb_clf_param = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'factor_num': 190.0, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 500.0, 'len_train': 4000.0, 'max_depth': 2, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'objective': 'binary:logistic', 'pct_threshold': 0.03180898829011758, 'random_state': 2022, 'refer_num': 1700.0, 'reg_alpha': 0, 'reg_lambda': 1, 'scale_pos_weight': 3, 'seed': 2022, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}

hyper_xgb_clf_params = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': 0.005,
    'max_depth': hp.choice('max_depth', list(range(2, 5))),
    'min_child_weight': 5,
    'n_estimators': 1000,
    'n_jobs': -1,
    'random_state': 2022,
    'objective': 'binary:logistic',
    'seed': 2022,
    'reg_alpha': hp.choice('reg_alpha', [1, 0]),
    'reg_lambda': hp.choice('reg_lambda', [1, 0]),
    'scale_pos_weight': 3,
    'silent': True,
    'subsample': hp.quniform('subsample', 0.7, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 120, 200, 10),
    'len_train': hp.quniform('len_train', 3000, 5500, 200),
    'len_test': hp.quniform('len_test', 400, 1500, 100),
    'pct_threshold': hp.uniform('pct_threshold', 0, 0.08),
    'refer_num': hp.quniform('refer_num', 100, 2000, 100)
}

multi_xgb_clf_params = {
    'booster': ['gbtree'],
    'gamma': [0.1],
    'learning_rate': [0.003, 0.004, 0.005],
    'max_depth': [3, 5],
    'min_child_weight': [5],
    'n_estimators': [1000],
    'n_jobs': [-1],
    'random_state': [2022],
    'seed': [2022],
    'reg_alpha': [1],
    'reg_lambda': [1],
    'scale_pos_weight': [3],
    'silent': [True],
    'subsample': [0.6000000000000001],
    'colsample_bytree': [1],
    'tree_method': ['gpu_hist'],

    # 自定义参数
    'factor_num': [190, 200, 210],
    'score_threshold': [-0.002, -0.001, -0.005]
}

model_params = {
    'xgb_clf_model': xgb_clf_param
}
