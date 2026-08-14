# coding: utf-8
# Author：fengchi863
# Date ：2021/3/24 14:44

import numpy as np
from hyperopt import hp
from hyperopt.pyll import scope
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC


@scope.define
def addfun(a, b=0):
    return a + b

debug = False

xgb_nthread = -1

hyperopt_param = {}

if debug:
    hyperopt_param['lr_max_evals'] = 1
    hyperopt_param['xgb_max_evals'] = 1
    hyperopt_param['lgb_max_evals'] = 1
    xgb_nthread = 1
    xgb_min_num_round = 5
    xgb_max_num_round = 10
    xgb_num_round_step = 5
    gbdt_min_num_round = 5
    gbdt_max_num_round = 10
    gbdt_num_round_step = 5
else:
    hyperopt_param['lr_max_evals'] = 200
    hyperopt_param['xgb_max_evals'] = 200
    hyperopt_param['lgb_max_evals'] = 200
    xgb_min_num_round = 10
    xgb_max_num_round = 500
    xgb_num_round_step = 10
    gbdt_min_num_round = 10
    gbdt_max_num_round = 500
    gbdt_num_round_step = 10


choiceDict = {
    'boosting_type': ['gbdt', 'rf', 'dart'],
    'penalty': ['l1', 'l2'],
}

###########param space###########
param_space_clf_lr = {
    'C': hp.loguniform('C', np.log(0.001), np.log(10)),
    'penalty': hp.choice('penalty', ['l2']),
    'class_weight': 'balanced',
    'n_jobs': -1
}

param_space_clf_xgboost = {
    'booster': 'gbtree',
    'objective': 'binary:logistic',
    'eval_metric': 'auc',
    'scale_pos_weight': 1,
    'lambda': hp.quniform('lambda', 0, 5, 0.05),
    'nthread': xgb_nthread,
    'eta': hp.quniform('eta', 0.01, 1, 0.01),
    'colsample_bytree': hp.quniform('colsample_bytree', 0.5, 0.9, 0.1),
    'max_depth': scope.addfun(hp.randint('max_depth', 47), 3),
    'subsample': 1.,
    'n_estimators': hp.quniform('n_estimators', xgb_min_num_round, \
                                xgb_max_num_round, xgb_num_round_step)
}


###### bset model param ######
best_param_clf_lr = {
    'C': 0.05500036818661201,
    'class_weight': 'balanced',
    'n_jobs': -1,
    'penalty': 'l2'
}

best_param_clf_xgboost = {
    'booster': 'gbtree',
    'colsample_bytree': 0.8,
    'eta': 0.19,
    'eval_metric': 'auc',
    'lambda': 2.2,
    'max_depth': 4,
    'n_estimators': 100,
    'nthread': -1,
    'objective': 'binary:logistic',
    'scale_pos_weight': 1,
    'subsample': 1
}

best_param_reg_lgb = {
    'max_depth': 5,
    'lambda': 2.2,
    'bagging_fraction': 0.95,
    'early_stopping_round': 30,
    'num_leaves': 8, # < 2 * max_depth
    'min_data_in_leaf': 1000,
    'min_bin': 50,
    'learning_rate': 0.03
}