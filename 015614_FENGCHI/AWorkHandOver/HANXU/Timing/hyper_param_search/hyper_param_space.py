# coding: utf-8
# Author：fengchi863
# Date ：2022/6/20 15:06

from hyperopt import hp

xgb_hyper_param_space = {
    'booster': 'gbtree',
    'eta': hp.uniform('eta', 0.1, 0.8),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 0.9),
    'max_depth': hp.choice('max_depth', list(range(5, 10))),
    'subsample': hp.uniform('subsample', 0.5, 1),
    'n_estimators': hp.quniform('n_estimators', 50, 150, 10),
    'gamma': hp.uniform('gamma', 0, 0.2),
    'min_child_weight': 1,
    'tree_method': 'gpu_hist',
    'sampling_method': 'gradient_based',
    'num_boost_round': 1000,
    'early_stopping_rounds': 200,
    'n_jobs': 10,   # 模型内部并行运算
    'eval_metric': 'mae',

    # 'select_num': hp.quniform('select_num', 300, 600, 100),
    'select_num': 400   # 已寻
}

best_hyper_param_space = {
    'booster': 'gbtree',
    'eta': 0.11551529526546109,
    'colsample_bytree': 0.8561865345374704,
    'max_depth': 4,
    'subsample': 0.7594876145527114,
    'n_estimators': 80,
    'gamma': 0.08976237191671696,
    'min_child_weight': 1,
    'tree_method': 'gpu_hist',
    'sampling_method': 'gradient_based',
    'num_boost_round': 1000,
    'early_stopping_rounds': 200,
    'n_jobs': 10,   # 模型内部并行运算
    'eval_metric': 'mae',

    'select_num': 400   # 已寻
}