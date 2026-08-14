# coding: utf-8
# Author：fengchi863

DEBUG = False

def gen_arith_sequ(start, end, interval):
    gen_list = list()
    val = start
    while val <= end:
        gen_list.append(val)
        val += interval
    return gen_list

hyper_xgb_reg_params = {
    'booster': 'gbtree',
    'objective': 'reg:linear',
    'gamma': 0,
    'eta': 0.005,
    'max_depth': 7,
    'min_child_weight': 3,
    'num_boost_round': 1000,
    'n_jobs': -1,
    # 'random_state': 2022,
    'eval_metric': 'rmse',
    'evals_result': 'auc',
    'alpha': 0.2,
    'lambda': 0.4,
    'scale_pos_weight': 1.0,
    'silent': True,
    'subsample': 0.6,
    'colsample_bytree': 0.5,
    'tree_method': 'gpu_hist',
}

fixed_xgb_reg_param = "{'alpha': 2.8, 'booster': 'gbtree', 'colsample_bytree': 0.9, 'eta': 0.018, 'eval_metric': 'rmse', " \
                      "'evals_result': ('auc', 'rmse'), 'gamma': 0, 'lambda': 0.6, 'max_depth': 6, 'min_child_weight': 10, " \
                      "'n_jobs': -1, 'num_boost_round': 1050.0, 'objective': 'reg:linear', 'seed': 2022, " \
                      "'scale_pos_weight': 1.0, 'silent': True, 'subsample': 1, 'tree_method': 'gpu_hist'}"

hyper_lgb_reg_params = {
    'boosting_type': 'gbdt',
    'class_weight': None,
    'colsample_bytree': 0.5,    # 构建弱学习器时，对特征随机采样的比例，默认值为1
    'learning_rate': 0.005,
    'max_depth': 6,
    'min_child_samples': 4,
    'min_child_weight': 0.001,  # 指定子节点中最小的样本权重和，如果一个叶子节点的样本权重和小于min_child_weight则拆分过程结束，默认值为1。推荐的候选值为：[1, 3, 5, 7]
    'min_split_gain': 0.0,  # 指定叶节点进行分支所需的损失减少的最小值，默认值为0。设置的值越大，模型就越保守。
    'n_estimators': 1000 if not DEBUG else 200,
    'n_jobs': -1,
    'verbosity': -1,    # 对于sklearn API 这个参数是silent，对于原生lgb，参数是verbosity
    'metric': {'binary_logloss', 'auc'},
    'num_leaves': 36,
    'random_state': 2022,
    'reg_alpha': 1.0,
    'reg_lambda': 0.6,
    'subsample': 0.9,
    'subsample_freq': 0, # 数值型，默认值0，表示禁用样本采样
    'device': 'gpu',
    'gpu_platform_id': 1,
    'gpu_device_id': 0,
    'gpu_use_dp': True,
}

fixed_lgb_reg_param = "{'boosting_type': 'gbdt', 'class_weight': None, 'colsample_bytree': 0.9,  'learning_rate': 0.02, 'max_depth': 5,\
    'min_child_samples': 4, 'min_child_weight': 0.001, 'min_split_gain': 0.0, 'n_estimators': 800,\
    'n_jobs': -1, 'verbosity': -1, 'metric': {'binary_logloss', 'auc'}, 'num_leaves': 36, 'seed': 2022,\
    'reg_alpha': 2.0, 'reg_lambda': 0.6, 'subsample': 1, 'subsample_freq': 0,  'device': 'gpu',\
    'gpu_platform_id': 1, 'gpu_device_id': 0, 'gpu_use_dp': True,\
}"

# hyper_lgb_clf_params = {
#     'boosting_type': 'gbdt',
#     'objective': 'binary',
#     'class_weight': None,
#     'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 1, 0.1),    # 构建弱学习器时，对特征随机采样的比例，默认值为1
#     'learning_rate': 0.005,
#     'max_depth': hp.quniform('max_depth', 3, 9, 1),
#     'min_child_samples': hp.quniform('min_child_samples', 1, 20, 2),
#     'min_child_weight': 0.001,  # 指定子节点中最小的样本权重和，如果一个叶子节点的样本权重和小于min_child_weight则拆分过程结束，默认值为1。推荐的候选值为：[1, 3, 5, 7]
#     'min_split_gain': 0.0,  # 指定叶节点进行分支所需的损失减少的最小值，默认值为0。设置的值越大，模型就越保守。
#     'n_estimators': hp.quniform('n_estimators', 2000, 4000, 100) if not DEBUG else hp.quniform('n_estimators', 100, 200, 10),
#     'n_jobs': -1,
#     'verbosity': -1,    # 对于sklearn API 这个参数是silent，对于原生lgb，参数是verbosity
#     'metric': {'binary_logloss', 'auc'},
#     'num_leaves': hp.quniform('num_leaves', 2, 40, 4),
#     'random_state': 2022,
#     'reg_alpha': hp.quniform('reg_alpha', 0, 1, 0.1),
#     'reg_lambda': hp.quniform('reg_lambda', 0, 1, 0.1),
#     'subsample': hp.quniform('subsample', 0.5, 1, 0.1),
#     'subsample_freq': 0, # 数值型，默认值0，表示禁用样本采样
#     'device': 'gpu',
#     'gpu_platform_id': 1,
#     'gpu_device_id': 0,
#     'gpu_use_dp': True,
# }
#
# hyper_cat_reg_params = {
#     'loss_function': hp.choice('loss_function', ['RMSE']),
#     'iterations': hp.quniform('iterations', 800, 1500, 100),
#     'learning_rate': 0.005,
#     'random_seed': 2025,
#     'l2_leaf_reg': hp.quniform('l2_leaf_reg', 0, 1, 0.1),
#     'depth': hp.quniform('depth', 3, 9, 1),
#     'leaf_estimation_method': 'Gradient',
#     'nan_mode': 'Forbidden',
#     'boosting_type': hp.choice('boosting_type', ['Ordered', 'Plain']),  # 排序提升，经典提升
#     'logging_level': 'Silent',
#     'eval_metric': 'AUC',
#     'feature_border_type': hp.choice('feature_border_type', ['GreedyLogSum', 'MinEntropy']),
#     'task_type': 'GPU',
#     'devices': '0:1'
# }
#
hyper_lr_reg_params = {
    'normalize': True,
    'fit_intercept': False,
    'n_jobs': 10
}

fixed_lr_reg_params = {''}