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

xgb_reg_param_ = {
    'booster': 'gbtree',
    'gamma': 0.1,     # 用于控制是否后剪枝的参数,越大越保守，一般0.1、0.2
    'learning_rate': 0.005,
    'max_depth': 3,
    'min_child_weight': 1,
    'n_estimators': 1000,
    'n_jobs': -1,
    'max_delta_step': 0,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': 1,
    'reg_lambda': 1,
    'scale_pos_weight': 3,
    'silent': True,
    'subsample': 0.8,
    'colsample_bytree': 0.8,
    'tree_method': 'gpu_hist',

    'factor_num': 200,
    'score_threshold': -0.001
}

xgb_reg_param0 = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'factor_num': 540.0, 'gamma': 0.1, 'learning_rate': 0.025, 'max_depth': 3, 'min_child_weight': 5.0, 'n_estimators': 740.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.9, 'reg_lambda': 0.9, 'scale_pos_weight': 3.0, 'score_threshold': -0.016163702391287803, 'seed': 2022, 'silent': True, 'subsample': 0.7000000000000001, 'tree_method': 'gpu_hist'}
# 19 91870000 fit很差
xgb_reg_param1 = {'booster': 'gbtree', 'colsample_bytree': 0.7000000000000001, 'factor_num': 500.0, 'gamma': 0.1, 'learning_rate': 0.011, 'max_depth': 4, 'min_child_weight': 5.0, 'n_estimators': 660.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1.0, 'reg_lambda': 0.6000000000000001, 'scale_pos_weight': 2.0, 'score_threshold': -0.009715353060976428, 'seed': 2022, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}
# 28 83630000 fit 6.28 36780000
xgb_reg_param2222 = {'booster': 'gbtree', 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 3, 'min_child_weight': 5, 'n_estimators': 900, 'n_jobs': -1, 'random_state': 2022, 'seed': 2022, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'silent': True, 'subsample': 0.6000000000000001, 'colsample_bytree': 1, 'tree_method': 'gpu_hist', 'factor_num': 470, 'score_threshold': -0.001}
# 29 89690000 fit 2 26750000 3.7 30860000
xgb_reg_param3 = {'booster': 'gbtree', 'colsample_bytree': 0.65, 'factor_num': 570.0, 'gamma': 0.1, 'learning_rate': 0.01, 'max_depth': 6, 'min_child_weight': 5.0, 'n_estimators': 840.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1.0, 'reg_lambda': 0.30000000000000004, 'scale_pos_weight': 3.0, 'score_threshold': -0.007719310697108288, 'seed': 2022, 'silent': True, 'subsample': 0.9, 'tree_method': 'gpu_hist'}
# 23 82560000 fit 4 31870000
xgb_reg_param4 = {'booster': 'gbtree', 'colsample_bytree': 0.75, 'factor_num': 560.0, 'gamma': 0.1, 'learning_rate': 0.013000000000000001, 'max_depth': 2, 'min_child_weight': 5.0, 'n_estimators': 800.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.9, 'reg_lambda': 0.6000000000000001, 'scale_pos_weight': 3.0, 'score_threshold': -0.00729686575676738, 'seed': 2022, 'silent': True, 'subsample': 0.6000000000000001, 'tree_method': 'gpu_hist'}
# 26 83900000 fit 4 27000000
xgb_reg_param5 = {'booster': 'gbtree', 'colsample_bytree': 0.7000000000000001, 'factor_num': 550.0, 'gamma': 0.1, 'learning_rate': 0.008, 'max_depth': 3, 'min_child_weight': 6.0, 'n_estimators': 760.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.6000000000000001, 'reg_lambda': 0.8, 'scale_pos_weight': 3.0, 'score_threshold': -0.006152598304606553, 'seed': 2022, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}

# 全部样本不对齐
xgb_reg_param00 = {'booster': 'gbtree', 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'random_state': 2022, 'seed': 2022, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'silent': True, 'subsample': 0.6000000000000001, 'colsample_bytree': 1, 'tree_method': 'gpu_hist', 'factor_num': 190, 'score_threshold': -0.001}
# test 5.16 1.6e fit 2.2 90430000  更改为滚动以后3.68 1.28e
xgb_reg_param11111 = {'booster': 'gbtree', 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'random_state': 2022, 'seed': 2022, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'silent': True, 'subsample': 0.6000000000000001, 'colsample_bytree': 1, 'tree_method': 'gpu_hist', 'factor_num': 200, 'score_threshold': 0.008}
# test 7 1.35e  fit 1.67 55830000
xgb_reg_param22 = {'booster': 'gbtree', 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'random_state': 2022, 'seed': 2022, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'silent': True, 'subsample': 0.6000000000000001, 'colsample_bytree': 1, 'tree_method': 'gpu_hist', 'factor_num': 200, 'score_threshold': -0.001}
# 自己调试参数测试
xgb_reg_param33 = {'booster': 'gbtree', 'gamma': 0.1, 'learning_rate': 0.005, 'max_depth': 3, 'min_child_weight': 5, 'n_estimators': 1200, 'n_jobs': -1, 'random_state': 2022, 'seed': 2022, 'reg_alpha': 0, 'reg_lambda': 1, 'scale_pos_weight': 3, 'silent': True, 'subsample': 0.6000000000000001, 'colsample_bytree': 1, 'tree_method': 'gpu_hist', 'factor_num': 200, 'score_threshold': 0}

# 改为滚动训练以后第一轮 20.17 8930w | 4.16 5716w
xgb_reg_param000 = {'booster': 'gbtree', 'colsample_bytree': 1, 'factor_num': 200, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 1300.0, 'len_train': 8000.0, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'pct_threshold': 0.05907025488829584, 'random_state': 2022, 'refer_num': 300.0, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'seed': 2022, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}
# 和上一个参数只改动了滚动区间长度 20.42 11480w
xgb_reg_param111 = {'booster': 'gbtree', 'colsample_bytree': 1, 'factor_num': 200, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 1300.0, 'len_train': 8000.0, 'max_depth': 5, 'min_child_weight': 5, 'n_estimators': 1000, 'n_jobs': -1, 'pct_threshold': 0.040962046550346534, 'random_state': 2022, 'refer_num': 400.0, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'seed': 2022, 'silent': True, 'subsample': 0.6, 'tree_method': 'gpu_hist'}
# 20220728选出 8.5299 9851w | 13.41 8038w  改进版 费率0.003
xgb_reg_param = {'booster': 'gbtree', 'colsample_bytree': 0.9, 'factor_num': 190.0, 'gamma': 0.1, 'learning_rate': 0.005, 'len_test': 1400.0, 'len_train': 8000.0, 'max_depth': 3, 'min_child_weight': 5.0, 'n_estimators': 1000, 'n_jobs': -1, 'pct_threshold': 0.04603695817905007, 'random_state': 2022, 'refer_num': 1500.0, 'reg_alpha': 1, 'reg_lambda': 1, 'scale_pos_weight': 3, 'seed': 2022, 'silent': True, 'subsample': 0.8, 'tree_method': 'gpu_hist'}
hyper_xgb_reg_params0 = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': hp.quniform('learning_rate', 0.001, 0.02, 0.001),
    'max_depth': hp.choice('max_depth', list(range(2, 7))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': hp.quniform('n_estimators', 800, 1200, 20),
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.quniform('reg_alpha', 0, 1, 0.1),
    'reg_lambda': hp.quniform('reg_lambda', 0, 1, 0.1),
    'scale_pos_weight': hp.quniform('scale_pos_weight', 1, 4, 1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.4, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.05),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 200, 570, 10),
    'len_train': hp.quniform('len_train', 4000, 8000, 1000),
    'len_test': hp.quniform('len_test', 400, 1500, 100),
    'pct_threshold': hp.uniform('pct_threshold', 0.03, 0.08),
    'refer_num': hp.quniform('refer_num', 100, 2000, 100)
}

hyper_xgb_reg_params_____best_before_debug = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': 0.005,
    'max_depth': hp.choice('max_depth', list(range(2, 5))),
    'min_child_weight': hp.quniform('min_child_weight', 3, 6, 1),
    'n_estimators': 1000,
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': hp.choice('reg_alpha', [1, 0]),
    'reg_lambda': hp.choice('reg_lambda', [1, 0]),
    'scale_pos_weight': 3,
    'silent': True,
    'subsample': hp.quniform('subsample', 0.7, 1, 0.1),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.6, 1, 0.1),
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': hp.quniform('factor_num', 120, 200, 10),
    'len_train': hp.quniform('len_train', 4000, 8000, 1000),
    'len_test': hp.quniform('len_test', 500, 2000, 100),
    'pct_threshold': hp.uniform('pct_threshold', 0, 0.08),
    'refer_num': hp.quniform('refer_num', 100, 2000, 100)
}

hyper_xgb_reg_params = {
    'booster': 'gbtree',
    'gamma': 0.1,
    'learning_rate': 0.005,
    'max_depth': 3,
    'min_child_weight': 5,
    'n_estimators': 1000,
    'n_jobs': -1,
    'random_state': 2022,
    'seed': 2022,
    'reg_alpha': 1,
    'reg_lambda': 1,
    'scale_pos_weight': 3,
    'silent': True,
    'subsample': 0.8,
    'colsample_bytree': 0.9,
    'tree_method': 'gpu_hist',

    # 自定义参数
    'factor_num': 190,
    'len_train': hp.quniform('len_train', 4000, 8000, 1000),
    'len_test': hp.quniform('len_test', 300, 2000, 100),
    'pct_threshold': hp.uniform('pct_threshold', 0, 0.08),
    'refer_num': hp.quniform('refer_num', 100, 1500, 100)
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
