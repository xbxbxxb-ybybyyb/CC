# coding: utf-8
# Author：fengchi863

from hyperopt import hp

_xgb_clf_param = {
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
# 14613680
xgb_clf_param2 = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'gamma': 0.4, 'learning_rate': 0.1, 'max_depth': 4, 'min_child_weight': 4.0, 'n_estimators': 160, 'n_jobs': -1, 'objective': 'binary:logistic', 'random_state': 2022, 'reg_alpha': 0.5, 'reg_lambda': 0.1, 'scale_pos_weight': 1, 'silent': True, 'subsample': 0.7000000000000001, 'tree_method': 'gpu_hist'}
# 33810715
xgb_clf_param3 = {'booster': 'gbtree', 'colsample_bytree': 0.6000000000000001, 'factor_num': 400, 'gamma': 0.1, 'learning_rate': 0.05, 'max_depth': 3, 'min_child_weight': 4.0, 'n_estimators': 200, 'n_jobs': -1, 'objective': 'binary:logistic', 'random_state': 2022, 'reg_alpha': 0, 'reg_lambda': 1, 'scale_pos_weight': 2.0, 'score_threshold': 0.5, 'silent': True, 'subsample': 0.6000000000000001, 'tree_method': 'gpu_hist', 'seed': 2022}
# 3.8515, 4.4817, 536.0, 42339732.4546, -10993091.0
xgb_clf_param = {'booster': 'gbtree',
                 'colsample_bytree': 0.8,
                 'factor_num': 500,
                 'gamma': 0.1,
                 'learning_rate': 0.04,
                 'max_depth': 3,
                 'min_child_weight': 3.0,
                 'n_estimators': 270,
                 'n_jobs': -1,
                 'objective': 'binary:logistic',
                 'random_state': 2022,
                 'reg_alpha': 0,
                 'reg_lambda': 0.5,
                 'scale_pos_weight': 3.0,
                 'score_threshold': 0.4996384384323199,
                 'silent': True,
                 'subsample': 0.9,
                 'tree_method': 'gpu_hist'}

hyper_xgb_clf_params = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': hp.choice('learning_rate', [0.01, 0.02, 0.03, 0.04, 0.05]),
    'max_depth': hp.choice('max_depth', list(range(2, 6))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 5, 1),
    'n_estimators': hp.quniform('n_estimators', 150, 300, 10),
    'n_jobs': -1,
    'objective': 'binary:logistic',
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.choice('reg_alpha', [0, 0.1, 0.5, 1]),
    'reg_lambda': hp.choice('reg_lambda', [0, 0.1, 0.5, 1]),
    'scale_pos_weight': hp.quniform('scale_pos_weight', 1, 3, 1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.6, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 450, 550, 10),
    'score_threshold': hp.uniform('score_threshold', 0.4, 0.6)
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
