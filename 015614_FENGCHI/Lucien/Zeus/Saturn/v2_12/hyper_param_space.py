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

xgb_reg_param0 = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'early_stopping_rounds': 300.0, 'factor_num': 250.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 5.0, 'min_child_weight': 6.0, 'n_estimators': 3000, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 1.0, 'score_threshold': 0.001, 'seed': 2022, 'silent': True, 'subsample': 1.0, 'tree_method': 'gpu_hist'}
xgb_reg_param1 = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'early_stopping_rounds': 200.0, 'factor_num': 250.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 5.0, 'min_child_weight': 3.0, 'n_estimators': 3000, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0, 'reg_lambda': 0, 'scale_pos_weight': 1.0, 'score_threshold': 0.01, 'seed': 2022, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}
xgb_reg_param = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'early_stopping_rounds': 900.0, 'factor_num': 270.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 5.0, 'min_child_weight': 6.0, 'n_estimators': 3000, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1, 'reg_lambda': 0.5, 'scale_pos_weight': 1.0, 'score_threshold': 0.002, 'seed': 2022, 'silent': True, 'subsample': 1.0, 'tree_method': 'gpu_hist'}

hyper_xgb_reg_params = {
    'booster': 'gbtree',
    'gamma': 0,
    'learning_rate': 0.005,
    'max_depth': hp.quniform('max_depth', 3, 5, 1),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': 3000,
    'early_stopping_rounds': hp.quniform('early_stopping_rounds', 200, 1000, 100),
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.choice('reg_alpha', [1, 0.5, 0]),
    'reg_lambda': hp.choice('reg_lambda', [1, 0.5, 0]),
    'scale_pos_weight': 1.0,
    'silent': True,
    'subsample': hp.quniform('subsample', 0.7, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.7, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 非模型参数
    'score_threshold': hp.quniform('score_threshold', -0.01, 0.01, 0.001),
    'factor_num': hp.quniform('factor_num', 180, 300, 10),
}

hyper_xgb_reg_params_4fit = {
    'booster': 'gbtree',
    'gamma': 0,
    'learning_rate': 0.005,
    'max_depth': 5,
    'min_child_weight': 6,
    'n_estimators': 3000,
    'early_stopping_rounds': 300,
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': 1,
    'reg_lambda': 1,
    'scale_pos_weight': 1.0,
    'silent': True,
    'subsample': 1,
    'colsample_bytree': 1,
    'tree_method': 'gpu_hist',

    # 非模型参数
    'score_threshold': hp.quniform('score_threshold', -0.01, 0.01, 0.0001),
    'factor_num': 250,
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
