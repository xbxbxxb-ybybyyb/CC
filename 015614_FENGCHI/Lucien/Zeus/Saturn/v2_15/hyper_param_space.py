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

# 20220816 测试结果
xgb_reg_param = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'early_stopping_rounds': 400, 'factor_num': 190.0, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 600.0, 'len_train': 8000, 'max_depth': 4, 'min_child_weight': 4.0, 'n_estimators': 2000, 'n_jobs': -1, 'pct_threshold': 0.031206600643744052, 'random_state': 2022, 'refer_num': 500, 'reg_alpha': 0.5, 'reg_lambda': 0, 'scale_pos_weight': 2.0, 'seed': 2022, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}

hyper_xgb_reg_params = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': 0.005,
    'max_depth': hp.choice('max_depth', list(range(2, 5))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': 3000,
    'early_stopping_rounds': 400,
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.choice('reg_alpha', [1, 0.5, 0]),
    'reg_lambda': hp.choice('reg_lambda', [1, 0.5, 0]),
    'scale_pos_weight': hp.quniform('scale_pos_weight', 0, 4, 1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.7, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 120, 200, 10),
    'len_train': 8000,
    'len_test': 500,
    'pct_threshold': hp.uniform('pct_threshold', 0, 0.08),
    'refer_num': 500
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
