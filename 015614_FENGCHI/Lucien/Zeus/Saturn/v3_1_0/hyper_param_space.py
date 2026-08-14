# coding: utf-8
# Author：fengchi863

from hyperopt import hp


def gen_arith_sequ(start, end, interval):
    gen_list = list()
    val = start
    while val <= end:
        gen_list.append(val)
        val += interval
    return gen_list

lgb_reg_param = {}

xgb_reg_param = {'booster': 'gbtree', 'colsample_bytree': 0.7000000000000001, 'factor_num': 190.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 5.0, 'min_child_weight': 4.0, 'n_estimators': 1000, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.30000000000000004, 'reg_lambda': 0.0, 'scale_pos_weight': 1.0, 'score_threshold': 0.493947, 'silent': True, 'subsample': 0.7000000000000001, 'tree_method': 'gpu_hist'}
xgb_reg_param_fit = {'booster': 'gbtree', 'colsample_bytree': 0.9, 'factor_num': 260.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 5.0, 'min_child_weight': 6.0, 'n_estimators': 1000, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.8, 'reg_lambda': 0.4, 'scale_pos_weight': 1.0, 'score_threshold': 0.540159, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}

hyper_xgb_reg_params = {
    'booster': 'gbtree',
    'gamma': 0,
    'learning_rate': 0.005,
    'max_depth': hp.quniform('max_depth', 3, 5, 1),
    'min_child_weight': hp.quniform('min_child_weight', 1, 6, 1),
    'n_estimators': 1000,
    'n_jobs': -1,
    'random_state': 2022,
    'reg_alpha': hp.quniform('reg_alpha', 0, 1, 0.1),
    'reg_lambda': hp.quniform('reg_lambda', 0, 1, 0.1),
    'scale_pos_weight': 1.0,
    'silent': True,
    'subsample': hp.quniform('subsample', 0.5, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 非模型参数
    'score_threshold': -0.007,
    'factor_num': hp.quniform('factor_num', 150, 280, 10),

}

hyper_lgb_reg_params = {
    'boosting_type': 'gbdt',
    'class_weight': None,
    'colsample_bytree': 1.0,
    'importance_type': 'split',
    'learning_rate': 0.1,
    'max_depth': -1,
    'min_child_samples': 20,
    'min_child_weight': 0.001,
    'min_split_gain': 0.0,
    'n_estimators': 100,
    'n_jobs': -1,
    'num_leaves': 31,
    'objective': None,
    'random_state': None,
    'reg_alpha': 0.0,
    'reg_lambda': 0.0,
    'silent': True,
    'subsample': 1.0,
    'subsample_for_bin': 200000,
    'subsample_freq': 0
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
    'xgb_reg_model': xgb_reg_param,
    'lgb_reg_model': lgb_reg_param
}

model_params_fit = {
    'xgb_reg_model': xgb_reg_param_fit
}
