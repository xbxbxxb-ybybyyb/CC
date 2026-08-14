# coding: utf-8
# Author：fengchi863

def add(raw_params: dict, add_params):
    raw_params_copy = raw_params.copy()
    raw_params_copy.update(add_params)
    return raw_params_copy

xgb_fixed_params = {'booster': 'gbtree', 'colsample_bytree': 0.9, 'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'alpha': 2.8,
                    'min_child_weight': 10, 'n_jobs': -1, 'seed': 2022, 'scale_pos_weight': 1.0, 'silent': True,
                    'subsample': 1, 'tree_method': 'gpu_hist', 'eval_metric': 'rmse', 'objective': 'reg:linear', 'eta': 0.018, 'max_depth': 6, 'num_boost_round': 1000}

hyper_xgb_reg_params_list = \
    [add(xgb_fixed_params, {'num_boost_round': x}) for x in range(100, 1500, 100)] + \
    [add(xgb_fixed_params, {'max_depth': x}) for x in range(2, 7, 1)] + \
    [add(xgb_fixed_params, {'eta': x}) for x in [0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04]] + \
    [add(xgb_fixed_params, {'objective': x}) for x in ['reg:logistic', 'reg:gamma']]

fixed_xgb_reg_param = {
    'fsv8': add(xgb_fixed_params, {'eta': 0.018, 'max_depth': 6, 'num_boost_round': 1000, 'objective': 'reg:linear'}),
    'fsv10': add(xgb_fixed_params, {'eta': 0.018, 'max_depth': 6, 'num_boost_round': 1000, 'objective': 'reg:linear'}),
    'fsv11': add(xgb_fixed_params, {'eta': 0.02, 'max_depth': 5, 'num_boost_round': 1000, 'objective': 'reg:linear'}),
    'fsrs': add(xgb_fixed_params, {'eta': 0.025, 'max_depth': 6, 'num_boost_round': 1200, 'objective': 'reg:linear'}),
    'rffs': add(xgb_fixed_params, {'eta': 0.025, 'max_depth': 6, 'num_boost_round': 1200, 'objective': 'reg:linear'}),
}

lgb_fixed_params = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9, 'min_child_samples': 4,
                    'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'),
                    'num_leaves': 36, 'seed': 2022, 'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',
                     'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True}

hyper_lgb_reg_params_list = [
    add(lgb_fixed_params, {'learning_rate': 0.02, 'max_depth': 5, 'n_estimators': 800}),
    add(lgb_fixed_params, {'learning_rate': 0.015, 'max_depth': 5, 'n_estimators': 800}),
    add(lgb_fixed_params, {'learning_rate': 0.015, 'max_depth': 5, 'n_estimators': 1000}),
    add(lgb_fixed_params, {'learning_rate': 0.015, 'max_depth': 5, 'n_estimators': 1100}),
]

fixed_lgb_reg_param = {
    'fsv8': add(lgb_fixed_params, {'learning_rate': 0.02, 'max_depth': 5, 'n_estimators': 800}),
    'fsv10': add(lgb_fixed_params, {'learning_rate': 0.02, 'max_depth': 5, 'n_estimators': 800}),
    'fsv11': add(lgb_fixed_params, {'learning_rate': 0.015, 'max_depth': 5, 'n_estimators': 1100}),
    'fsrs': add(lgb_fixed_params, {'learning_rate': 0.015, 'max_depth': 5, 'n_estimators': 1100}),
    'rffs': add(lgb_fixed_params, {'learning_rate': 0.015, 'max_depth': 5, 'n_estimators': 1100}),
}

hyper_lr_reg_params = {
    'normalize': True,
    'fit_intercept': False,
    'n_jobs': 10
}

fixed_lr_reg_params = {''}