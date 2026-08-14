# coding: utf-8
# Author：fengchi863

import numpy as np
from itertools import product

def add(raw_params: dict, add_params):
    raw_params_copy = raw_params.copy()
    raw_params_copy.update(add_params)
    return raw_params_copy

#%% xgboost参数
xgb_fixed_params = {'booster': 'gbtree', 'colsample_bytree': 0.6, 'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.3, 'alpha': 1.2,
                    'min_child_weight': 8, 'n_jobs': -1, 'seed': 2022, 'scale_pos_weight': 1.0, 'silent': True,
                    'subsample': 0.6, 'tree_method': 'gpu_hist', 'eval_metric': 'rmse', 'objective': 'reg:linear', 'eta': 0.01, 'max_depth': 6, 'num_boost_round': 1000}

# hyper_xgb_reg_params_list = \
#     [add(xgb_fixed_params, {'num_boost_round': x}) for x in range(300, 2500, 200)] + \
#     [add(xgb_fixed_params, {'max_depth': x}) for x in range(3, 10, 1)] + \
#     [add(xgb_fixed_params, {'eta': x}) for x in [0.001, 0.005, 0.01, 0.015, 0.02, 0.025, 0.03, 0.04, 0.06, 0.08, 0.1, 0.15, 0.2]] + \
#     [add(xgb_fixed_params, {'colsample_bytree': x}) for x in [0.5, 0.6, 0.7, 0.8, 0.9, 1.0]] + \
#     [add(xgb_fixed_params, {'lambda': x}) for x in np.arange(0.1, 3, 0.4)] + \
#     [add(xgb_fixed_params, {'alpha': x}) for x in np.arange(0.1, 3, 0.4)] + \
#     [add(xgb_fixed_params, {'subsample': x}) for x in np.arange(0.1, 1, 0.1)]
#     # [add(xgb_fixed_params, {'gamma': x}) for x in [0, 0.2, 0.4, 0.6, 0.8, 1.0]] + \
#     # [add(xgb_fixed_params, {'min_child_weight': x}) for x in range(1, 11)] + \

hyper_xgb_reg_params_list = \
    [add(xgb_fixed_params, {'num_boost_round': x}) for x in range(100, 2000, 300)] + \
    [add(xgb_fixed_params, {'max_depth': x}) for x in range(3, 6, 1)] + \
    [add(xgb_fixed_params, {'eta': x}) for x in [0.003, 0.005, 0.01, 0.015, 0.02]] + \
    [add(xgb_fixed_params, {'colsample_bytree': x}) for x in [0.5, 0.75, 0.9]]
    # [add(xgb_fixed_params, {'lambda': x}) for x in np.arange(0.1, 3, 0.4)] + \
    # [add(xgb_fixed_params, {'alpha': x}) for x in np.arange(0.1, 3, 0.4)] + \
    # [add(xgb_fixed_params, {'subsample': x}) for x in np.arange(0.1, 1, 0.1)]
    # [add(xgb_fixed_params, {'gamma': x}) for x in [0, 0.2, 0.4, 0.6, 0.8, 1.0]] + \
    # [add(xgb_fixed_params, {'min_child_weight': x}) for x in range(1, 11)] + \

hyper_xgb_reg_params_space = (
    [('num_boost_round', x) for x in list(range(200, 2000, 400)) + list(range(2500, 5500, 1000))],
    [('max_depth', x) for x in [4, 5]],
    [('eta', x) for x in [0.01, 0.016]],
    # [('colsample_bytree', x) for x in [0.6, 0.9]]
)
hyper_xgb_reg_params_space = list(product(*(hyper_xgb_reg_params_space[idx] for idx in range(len(hyper_xgb_reg_params_space)))))
hyper_xgb_reg_params_list = list()
for idx in range(len(hyper_xgb_reg_params_space)):
    tmp_param = hyper_xgb_reg_params_space[idx]
    tmp_param_dict = dict(tmp_param)
    hyper_xgb_reg_params_list.append(add(xgb_fixed_params, tmp_param_dict))

# print(f'xgboost参数空间为{len(hyper_xgb_reg_params_list)}个')

fixed_xgb_reg_param = {
    'fsv8': add(xgb_fixed_params, {'eta': 0.012, 'max_depth': 5, 'num_boost_round': 450, 'seed': 2004}),
    'fsv10': add(xgb_fixed_params, {'eta': 0.018, 'max_depth': 6, 'num_boost_round': 430, 'seed': 2003}),
    'fsv11': add(xgb_fixed_params, {'eta': 0.02, 'max_depth': 5, 'num_boost_round': 480, 'subsample': 0.6, 'seed': 2002}),
    'fsrs': add(xgb_fixed_params, {'eta': 0.015, 'max_depth': 6, 'num_boost_round': 490, 'subsample': 0.5, 'min_child_weight': 7, 'seed': 2002}),
    'rffs': add(xgb_fixed_params, {'eta': 0.025, 'max_depth': 6, 'num_boost_round': 410, 'seed': 2002}),
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