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

xgb_clf_param1 = {
    'booster': 'gbtree',
    'gamma': 0.1,     # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2
    'learning_rate': 0.4,
    'max_depth': 3,     # 构建树的深度，越大越容易过拟合
    'min_child_weight': 1,
    'n_estimators': 50,
    'n_jobs': -1,
    'objective': 'binary:logistic',
    'random_state': 2022,
    'reg_alpha': 0,
    'reg_lambda': 1,
    'scale_pos_weight': 1,
    'silent': True,
    'subsample': 0.7,   # 随机采样训练样本
    'colsample_bytree': 0.7,    # 生成树时进行的列采样
    'lambda': 2,    # 控制模型复杂度的权重值的L2正则化项参数，参数越大，模型越不容易过拟合
    'tree_method': 'gpu_hist'   # 使用GPU
}

xgb_clf_param0 = {'booster': 'gbtree', 'colsample_bytree': 0.7000000000000001, 'factor_num': 450, 'gamma': 0.1, 'learning_rate': 0.025, 'max_depth': 5, 'min_child_weight': 4.0, 'n_estimators': 720, 'n_jobs': -1, 'objective': 'binary:logistic', 'random_state': 2022, 'reg_alpha': 0.1, 'reg_lambda': 1, 'scale_pos_weight': 4.0, 'score_threshold': 0.4261538353160572, 'seed': 2022, 'silent': True, 'subsample': 0.6000000000000001, 'tree_method': 'gpu_hist'}
xgb_clf_param2 = {'booster': 'gbtree', 'colsample_bytree': 0.6000000000000001, 'factor_num': 460.0, 'gamma': 0.1, 'learning_rate': 0.01, 'max_depth': 2, 'min_child_weight': 4.0, 'n_estimators': 260.0, 'n_jobs': -1, 'objective': 'binary:logistic', 'random_state': 2022, 'reg_alpha': 0, 'reg_lambda': 0.1, 'scale_pos_weight': 1.0, 'score_threshold': 0.5761293338947179, 'seed': 2022, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}
xgb_clf_param3 = {'booster': 'gbtree', 'colsample_bytree': 1.0, 'factor_num': 470.0, 'gamma': 0.1, 'learning_rate': 0.026000000000000002, 'max_depth': 3, 'min_child_weight': 4.0, 'n_estimators': 880.0, 'n_jobs': -1, 'objective': 'binary:logistic', 'random_state': 2022, 'reg_alpha': 1, 'reg_lambda': 0.1, 'scale_pos_weight': 3.0, 'score_threshold': 0.5196134671076511, 'seed': 2022, 'silent': True, 'subsample': 0.6000000000000001, 'tree_method': 'gpu_hist'}
xgb_clf_param = {'booster': 'gbtree', 'gamma': 0.1, 'learning_rate': 0.02, 'max_depth': 4, 'min_child_weight': 4, 'n_estimators': 700, 'n_jobs': -1, 'objective': 'binary:logistic', 'random_state': 2022, 'seed': 2022, 'reg_alpha': 1, 'reg_lambda': 0.1, 'scale_pos_weight': 3, 'silent': True, 'subsample': 0.6000000000000001, 'colsample_bytree': 0.8, 'tree_method': 'gpu_hist', 'factor_num': 470, 'score_threshold': 0.46}
hyper_xgb_clf_params = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': hp.quniform('learning_rate', 0.001, 0.03, 0.001),
    'max_depth': hp.choice('max_depth', list(range(2, 7))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': hp.quniform('n_estimators', 400, 1000, 20),
    'n_jobs': -1,
    'objective': 'binary:logistic',
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.quniform('reg_alpha', 0, 1, 0.1),
    'reg_lambda': hp.quniform('reg_lambda', 0, 1, 0.1),
    'scale_pos_weight': hp.quniform('scale_pos_weight', 1, 5, 1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.4, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 450, 570, 10),
    'score_threshold': hp.uniform('score_threshold', 0.4, 0.6)
}

multi_xgb_clf_params = {
    'booster': ['gbtree'],
    'gamma': [0.1],
    'learning_rate': [0.001, 0.003, 0.005, 0.01, 0.02],
    'max_depth': [3, 4],
    'min_child_weight': list(range(3, 5, 1)),
    'n_estimators': list(range(600, 1000, 100)),
    'n_jobs': [-1],
    'objective': ['binary:logistic'],
    'random_state': [2022],
    'seed': [2022],
    'reg_alpha': [1],
    'reg_lambda': [0.1],
    'scale_pos_weight': [3],
    'silent': [True],
    'subsample': [0.6000000000000001],
    'colsample_bytree': [1, 0.8],
    'tree_method': ['gpu_hist'],

    # 自定义参数
    'factor_num': [470],
    'score_threshold': [0.48, 0.46, 0.52]
}

lr_param = {
    'C': 1.0,
    'penalty': 'l1',    # l1耗时更长，l2耗时比l1短一些
    'class_weight': 'balanced'
}

linear_model_param = {
    'normalize': True
}

model_params = {
    'lr_model': lr_param,
    'linear_model': linear_model_param,
    'xgb_clf_model': xgb_clf_param,
}
