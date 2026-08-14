# coding: utf-8
# Author：fengchi863

hyper_xgb_reg_params_list = [
    {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.018, 'eval_metric': 'rmse',
         'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
         'n_jobs': -1, 'num_boost_round': 1000.0, 'objective': 'reg:linear', 'seed': 2022,
         'scale_pos_weight': 1.0, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
       'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
       'n_jobs': -1, 'num_boost_round': 1000.0, 'objective': 'reg:linear', 'seed': 2022,
       'scale_pos_weight': 1.0, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.02, 'eval_metric': 'rmse',
       'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 5, 'min_child_weight': 10,
       'n_jobs': -1, 'num_boost_round': 1000.0, 'objective': 'reg:linear', 'seed': 2022,
       'scale_pos_weight': 1.0, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
            'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
            'n_s': -1, 'num_boost_round': 1200.0, 'objective': 'reg:linear', 'seed': 2022,
            'scale_pos_weight': 0.6, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
]

fixed_xgb_reg_param = {
    'fsv8': {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
            'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
            'n_s': -1, 'num_boost_round': 1200.0, 'objective': 'reg:linear', 'seed': 2022,
            'scale_pos_weight': 0.6, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    'fsv10': {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
            'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
            'n_s': -1, 'num_boost_round': 1200.0, 'objective': 'reg:linear', 'seed': 2022,
            'scale_pos_weight': 0.6, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    'fsv11': {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
            'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
            'n_s': -1, 'num_boost_round': 1200.0, 'objective': 'reg:linear', 'seed': 2022,
            'scale_pos_weight': 0.6, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    'fsrs': {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
            'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
            'n_s': -1, 'num_boost_round': 1200.0, 'objective': 'reg:linear', 'seed': 2022,
            'scale_pos_weight': 0.6, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'},
    'rffs': {'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.025, 'eval_metric': 'rmse',
           'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10,
           'n_jobs': -1, 'num_boost_round': 1000.0, 'objective': 'reg:linear', 'seed': 2022,
           'scale_pos_weight': 1.0, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'}
}

hyper_lgb_reg_params_list = [
    {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9,  'learning_rate': 0.02, 'max_depth': 5,
     'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 800,
     'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
     'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',
     'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9,  'learning_rate': 0.015, 'max_depth': 5,
     'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 800,
     'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
     'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',
     'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9, 'learning_rate': 0.015, 'max_depth': 5,
     'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1000,
     'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
     'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0, 'device': 'gpu',
     'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9, 'learning_rate': 0.015, 'max_depth': 5,
     'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1100,
     'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
     'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0, 'device': 'gpu',
     'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
]

fixed_lgb_reg_param = {
    'fsv8': {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9, 'learning_rate': 0.015, 'max_depth': 5,
             'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1100,
             'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
             'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0, 'device': 'gpu',
             'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    'fsv10': {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9, 'learning_rate': 0.015, 'max_depth': 5,
             'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1100,
             'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
             'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0, 'device': 'gpu',
             'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    'fsv11': {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9,  'learning_rate': 0.02, 'max_depth': 5,
             'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 800,
             'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
             'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',
             'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    'fsrs': {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9, 'learning_rate': 0.015, 'max_depth': 5,
             'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1100,
             'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
             'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0, 'device': 'gpu',
             'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True},
    'rffs': {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9,  'learning_rate': 0.02, 'max_depth': 5,
             'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 800,
             'n_jobs': -1, 'verbosity': -1, 'metric': ('binary_logloss', 'auc'), 'num_leaves': 36, 'seed': 2022,
             'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',
             'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True}
}


hyper_lr_reg_params = {
    'normalize': True,
    'fit_intercept': False,
    'n_jobs': 10
}

fixed_lr_reg_params = {''}