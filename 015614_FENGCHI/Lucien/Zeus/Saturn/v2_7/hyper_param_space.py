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

xgb_reg_param0 = {
    'booster': 'gbtree',
    'gamma': 0.1,     # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2
    'learning_rate': 0.005,
    'max_depth': 3,
    'min_child_weight': 1,
    'n_estimators': 1000,
    'n_jobs': -1,
    'max_delta_step': 0,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': 1,
    'reg_lambda': 1,
    'scale_pos_weight': 3,
    'silent': True,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'tree_method': 'gpu_hist',

    'factor_num': 200,
    'score_threshold': -0.001
}

xgb_reg_param = {'booster': 'gbtree', 'colsample_bytree': 0.9, 'factor_num': 140.0, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 2000.0, 'len_train': 8000.0, 'max_depth': 2, 'min_child_weight': 3.0, 'n_estimators': 1000, 'n_jobs': -1, 'pct_threshold': 0.05457295148856585, 'random_state': 2022, 'refer_num': 1900.0, 'reg_alpha': 1, 'reg_lambda': 0, 'scale_pos_weight': 2.0, 'seed': 2022, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}

hyper_xgb_reg_params0 = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': hp.quniform('learning_rate', 0.001, 0.02, 0.001),
    'max_depth': hp.choice('max_depth', list(range(2, 7))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': hp.quniform('n_estimators', 800, 1200, 20),
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.quniform('reg_alpha', 0, 1, 0.1),
    'reg_lambda': hp.quniform('reg_lambda', 0, 1, 0.1),
    'scale_pos_weight': hp.quniform('scale_pos_weight', 1, 4, 1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.4, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.05),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 200, 570, 10),
    'len_train': hp.quniform('len_train', 4000, 8000, 1000),
    'len_test': hp.quniform('len_test', 400, 1500, 100),
    'pct_threshold': hp.uniform('pct_threshold', 0.03, 0.08),
    'refer_num': hp.quniform('refer_num', 100, 2000, 100)
}

hyper_xgb_reg_params = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': 0.005,
    'max_depth': hp.choice('max_depth', list(range(2, 5))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': 1000,
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.choice('reg_alpha', [1, 0]),
    'reg_lambda': hp.choice('reg_lambda', [1, 0]),
    'scale_pos_weight': hp.quniform('scale_pos_weight', 1, 4, 1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.7, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 120, 200, 10),
    'len_train': hp.quniform('len_train', 6000, 8000, 500),
    'len_test': hp.quniform('len_test', 500, 2000, 100),
    'pct_threshold': hp.uniform('pct_threshold', 0, 0.08),
    'refer_num': hp.quniform('refer_num', 100, 2000, 100)
}

multi_xgb_reg_params = {
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
    'xgb_reg_model': xgb_reg_param
}
