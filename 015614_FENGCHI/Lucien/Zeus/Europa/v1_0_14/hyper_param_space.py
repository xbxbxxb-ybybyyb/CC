# coding: utf-8
# Author：fengchi863

from hyperopt import hp
import collections
_dict = collections.OrderedDict

def gen_arith_sequ(start, end, interval):
    gen_list = list()
    val = start
    while val <= end:
        gen_list.append(val)
        val += interval
    return gen_list

xgb_reg_param ={'booster': 'gbtree', 'colsample_bytree': 0.8, 'factor_num': 300.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 3.0, 'min_child_weight': 6.0, 'n_estimators': 1200.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 1.0, 'reg_lambda': 0.7000000000000001, 'scale_pos_weight': 1.0, 'score_threshold': 0.003402, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}
xgb_reg_param_fit = {'booster': 'gbtree', 'colsample_bytree': 0.9, 'factor_num': 300.0, 'gamma': 0, 'learning_rate': 0.005, 'max_depth': 4.0, 'min_child_weight': 3.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'random_state': 2022, 'reg_alpha': 0.7000000000000001, 'reg_lambda': 0.0, 'scale_pos_weight': 1.0, 'score_threshold': 0.00298, 'silent': True, 'subsample': 0.5, 'tree_method': 'gpu_hist'}
lgb_reg_param = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.7000000000000001, 'device': 'gpu', 'factor_num': 300.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 6.0, 'min_child_samples': 4.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1500.0, 'n_jobs': -1, 'num_leaves': 36.0, 'random_state': 2022, 'reg_alpha': 0.1, 'reg_lambda': 0.30000000000000004, 'score_threshold': -0.003621, 'silent': True, 'subsample': 0.5, 'subsample_freq': 0}
lgb_reg_param_fit = {'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.5, 'device': 'gpu', 'factor_num': 300.0, 'gpu_device_id': 0, 'gpu_platform_id': 1, 'learning_rate': 0.005, 'max_depth': 5.0, 'min_child_samples': 6.0, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 1400.0, 'n_jobs': -1, 'num_leaves': 12.0, 'random_state': 2022, 'reg_alpha': 0.1, 'reg_lambda': 0.1, 'score_threshold': 0.00021, 'silent': True, 'subsample': 0.6000000000000001, 'subsample_freq': 0}
lr_reg_param = {'factor_num': 300.0, 'fit_intercept': False, 'n_jobs': 10, 'normalize': False, 'score_threshold': 0}
lr_reg_param_fit = {'factor_num': 300.0, 'fit_intercept': False, 'n_jobs': 10, 'normalize': False, 'score_threshold': 0}

hyper_xgb_reg_params = _dict({
    'score_threshold': -0.000122,

    'booster': 'gbtree',
    'gamma': 0,
    'learning_rate': 0.005,
    'max_depth': hp.quniform('max_depth', 3, 5, 1),
    'min_child_weight': hp.quniform('min_child_weight', 1, 6, 1),
    'n_estimators': hp.quniform('n_estimators', 800, 1500, 100),
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
    'factor_num': hp.quniform('factor_num', 290, 300, 10),
})

hyper_lgb_reg_params = {
    'score_threshold': 0,

    'boosting_type': 'gbdt',
    'class_weight': None,
    'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 1, 0.1),    # 构建弱学习器时，对特征随机采样的比例，默认值为1
    'learning_rate': 0.005,
    'max_depth': hp.quniform('max_depth', 3, 9, 1),
    'min_child_samples': hp.quniform('min_child_samples', 1, 20, 2),
    'min_child_weight': 0.001,  # 指定子节点中最小的样本权重和，如果一个叶子节点的样本权重和小于min_child_weight则拆分过程结束，默认值为1。推荐的候选值为：[1, 3, 5, 7]
    'min_split_gain': 0.0,  # 指定叶节点进行分支所需的损失减少的最小值，默认值为0。设置的值越大，模型就越保守。
    'n_estimators': hp.quniform('n_estimators', 800, 1500, 100),
    'n_jobs': -1,
    'num_leaves': hp.quniform('num_leaves', 2, 40, 4),
    'random_state': 2022,
    'reg_alpha': hp.quniform('reg_alpha', 0, 1, 0.1),
    'reg_lambda': hp.quniform('reg_lambda', 0, 1, 0.1),
    'silent': True,
    'subsample': hp.quniform('subsample', 0.5, 1, 0.1),
    'subsample_freq': 0, # 数值型，默认值0，表示禁用样本采样
    'device': 'gpu',
    'gpu_platform_id': 1,
    'gpu_device_id': 0,

    'factor_num': hp.quniform('factor_num', 290, 300, 10),
}

hyper_lr_reg_params = {
    'score_threshold': 0,
    'normalize': hp.choice('normalize', [True, False]),
    'fit_intercept': hp.choice('fit_intercept', [True, False]),
    'n_jobs': 10,

    'factor_num': hp.quniform('factor_num', 290, 300, 10),
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
multi_lgb_reg_params = {}
multi_lr_reg_params = {}

model_params = {
    'xgb_reg_model': xgb_reg_param,
    'lgb_reg_model': lgb_reg_param,
    'lr_reg_model': lr_reg_param
}

model_params_fit = {
    'xgb_reg_model': xgb_reg_param_fit,
    'lgb_reg_model': lgb_reg_param_fit,
    'lr_reg_model': lr_reg_param_fit
}
