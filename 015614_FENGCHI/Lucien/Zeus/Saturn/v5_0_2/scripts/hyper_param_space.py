# coding: utf-8
# Author：fengchi863

import numpy as np

def add(raw_params: dict, add_params):
    raw_params_copy = raw_params.copy()
    raw_params_copy.update(add_params)
    return raw_params_copy

#%% xgboost参数
xgb_fixed_params = {'booster': 'gbtree', 'colsample_bytree': 0.6, 'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.3, 'alpha': 1.2,
                    'min_child_weight': 8, 'n_jobs': -1, 'seed': 2022, 'scale_pos_weight': 1.0, 'silent': True,
                    'subsample': 0.6, 'tree_method': 'gpu_hist', 'eval_metric': 'rmse', 'objective': 'reg:linear', 'eta': 0.01, 'max_depth': 6, 'num_boost_round': 1000}

hyper_xgb_reg_params_list = \
    [add(xgb_fixed_params, {'num_boost_round': x}) for x in range(300, 2500, 200)] + \
    [add(xgb_fixed_params, {'max_depth': x}) for x in range(3, 10, 1)] + \
    [add(xgb_fixed_params, {'eta': x}) for x in [0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2]] + \
    [add(xgb_fixed_params, {'colsample_bytree': x}) for x in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]] + \
    [add(xgb_fixed_params, {'lambda': x}) for x in np.arange(0.1, 3, 0.4)] + \
    [add(xgb_fixed_params, {'alpha': x}) for x in np.arange(0.1, 3, 0.4)] + \
    [add(xgb_fixed_params, {'subsample': x}) for x in np.arange(0.1, 1, 0.1)]
    # [add(xgb_fixed_params, {'gamma': x}) for x in [0, 0.2, 0.4, 0.6, 0.8, 1.0]] + \
    # [add(xgb_fixed_params, {'min_child_weight': x}) for x in range(1, 11)] + \

fixed_xgb_reg_param = {
    'fsv8': add(xgb_fixed_params, {'eta': 0.012, 'max_depth': 5, 'num_boost_round': 900, 'seed': 2003}),   # config3
    'fsv10': add(xgb_fixed_params, {'eta': 0.018, 'max_depth': 6, 'num_boost_round': 1200, 'seed': 2003}),  # config1
    'fsv11': add(xgb_fixed_params, {'eta': 0.02, 'max_depth': 5, 'num_boost_round': 3000, 'subsample': 0.6, 'seed': 2001}),  # config2
    'fsrs': add(xgb_fixed_params, {'eta': 0.015, 'max_depth': 6, 'num_boost_round': 500, 'subsample': 0.5, 'min_child_weight': 7, 'seed': 2002}),
    'rffs': add(xgb_fixed_params, {'eta': 0.025, 'max_depth': 6, 'num_boost_round': 660}),
    'fsci': add(xgb_fixed_params, {'eta': 0.016, 'max_depth': 5, 'num_boost_round': 1800, 'sedd': 2001}),  # config2
}

#%% lightgbm参数
lgb_fixed_params = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.6, 'min_child_samples': 4,
                    'min_child_weight': 10, 'min_split_gain': 0.0, 'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'),
                    'num_leaves': 36, 'seed': 2022, 'reg_alpha': 2.5, 'reg_lambda': 2.5, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',
                     'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True, 'n_estimators': 800, 'max_depth': 3, 'learning_rate': 0.04}

hyper_lgb_reg_params_list = \
    [add(lgb_fixed_params, {'n_estimators': x}) for x in range(300, 2500, 200)] + \
    [add(lgb_fixed_params, {'max_depth': x}) for x in range(3, 10, 1)] + \
    [add(lgb_fixed_params, {'learning_rate': x}) for x in [0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2]] + \
    [add(lgb_fixed_params, {'colsample_bytree': x}) for x in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]] + \
    [add(lgb_fixed_params, {'reg_lambda': x}) for x in np.arange(0.1, 3, 0.4)] + \
    [add(lgb_fixed_params, {'reg_alpha': x}) for x in np.arange(0.1, 3, 0.4)] + \
    [add(lgb_fixed_params, {'min_child_weight': x}) for x in range(1, 11)]

fixed_lgb_reg_param = {
    'fsv8': add(lgb_fixed_params, {'learning_rate': 0.04, 'max_depth': 4, 'n_estimators': 1400, 'seed': 2003}),
    'fsv10': add(lgb_fixed_params, {'learning_rate': 0.03, 'max_depth': 4, 'n_estimators': 1100, 'seed': 2002}),
    'fsv11': add(lgb_fixed_params, {'learning_rate': 0.035, 'max_depth': 4, 'n_estimators': 1000}),
    'fsrs': add(lgb_fixed_params, {'learning_rate': 0.325, 'max_depth': 4, 'n_estimators': 1000, 'seed': 2003}),
    'rffs': add(lgb_fixed_params, {'learning_rate': 0.3, 'max_depth': 4, 'n_estimators': 800, 'seed': 2001}),
}

#%% lr参数
hyper_lr_reg_params = {
    'normalize': True,
    'fit_intercept': False,
    'n_jobs': 10
}

fixed_lr_reg_params = {''}


mlp_reg_fixed_params = {'input_dim': 398, 'hidden_dim': 256, 'dropout': 0.2, 'layers': 3, 'epochs': 10,
                        'lr': 1e-4, 'batch_size': 512, 'wd': 1e-4, 'seed': 0}

hyper_mlp_reg_params_list = [
    add(mlp_reg_fixed_params, {'epochs': 1}),
]

fixed_mlp_reg_param = {
    'fsv8': add(mlp_reg_fixed_params, {'epochs': 10}),
    'fsv10': add(mlp_reg_fixed_params, {'epochs': 10}),
    'fsv11': add(mlp_reg_fixed_params, {'epochs': 10}),
    'fsrs': add(mlp_reg_fixed_params, {'epochs': 10}),
    'rffs': add(mlp_reg_fixed_params, {'epochs': 10}),
}