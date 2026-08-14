# coding: utf-8
# Author：fengchi863
# Date ：2020/5/22 13:52

import numpy as np
from hyperopt import hp
from hyperopt.pyll import scope
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC

from TrainingModel.AdaBoost import AdaBoostModelTree, AdaBoostModelNonTree
from TrainingModel.GBDT import GBDTModel
from TrainingModel.LogisticRegression import RollingLRModel
from TrainingModel.MLP import MLPModel
from TrainingModel.RF import RFModel
from TrainingModel.SVM import SVM
from TrainingModel.XGBoost import XGBModel


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

param_space_clf_lightgbm = {
    'boosting_type': hp.choice('boosting_type', choiceDict['boosting_type']),
    'objective': 'binary',
    'eval_metric': 'auc',
    'reg_lambda': hp.quniform('reg_lambda', 0, 5, 0.05),
    'nthread': xgb_nthread,
    'learning_rate': hp.quniform('learning_rate', 0.01, 1, 0.01),
    'feature_fraction': hp.uniform("feature_fraction", 0.5, 0.9),
    'max_depth': scope.addfun(hp.randint('max_depth', 7), 3),
    'num_leaves': scope.addfun(hp.randint('num_leaves', 223), 32),
    'bagging_fraction': hp.quniform("bagging_fraction", 0.2, 0.8, 0.1),
    'bagging_freq': scope.addfun(hp.randint('bagging_freq', 7), 2),
    'n_estimators': hp.quniform("n_estimators", xgb_min_num_round, \
                                xgb_max_num_round, xgb_num_round_step)
}

param_space_clf_svm = {
    'kernel': hp.choice('kernel', ['sigmoid', 'poly']),
    'degree': scope.addfun(hp.randint('degree', 2), 2),
    'tol': hp.loguniform('tol', -5, -2),
    'cache_size': 600,
    'class_weight': 'balanced'
}

param_space_clf_rf = {
    'n_estimators': hp.quniform("n_estimators", gbdt_min_num_round, \
                                gbdt_max_num_round, gbdt_num_round_step),
    'max_depth': scope.addfun(hp.randint('max_depth', 50), 3),
    'max_features': "auto",
    'class_weight': 'balanced'
}

param_space_clf_gbdt = {
    'learning_rate': hp.quniform('learning_rate', 0.01, 1, 0.01),
    'n_estimators': hp.quniform("n_estimators", gbdt_min_num_round, \
                                gbdt_max_num_round, gbdt_num_round_step),
    'subsample': hp.quniform('subsample', 0.6, 1, 0.1),
    'loss': 'deviance',
    'max_features': "auto",
    'max_depth': scope.addfun(hp.randint('max_depth', 100), 3),
}

param_space_clf_mlp = {
    'hidden_layer_sizes': hp.choice('hidden_layer_sizes', [(16, 8, 8), (8, 8), (16, 32, 8), (16, 8), (8, 4)]),
    'activation': hp.choice('activation', ['relu', 'logistic']),
    'alpha': hp.loguniform('alpha', np.log(0.000001), np.log(0.01)),
    'learning_rate': 'adaptive',
    'solver': 'sgd',
    'learning_rate_init': hp.loguniform('learning_rate_init', np.log(0.0001), np.log(0.1)),
    'momentum': hp.loguniform('momentum', np.log(0.1), np.log(0.7))
}

param_space_clf_adaboost_tree = {
    'n_estimators': scope.addfun(hp.randint('n_estimators', 60), 30),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.05), np.log(5)),
    ############当base_estimator为决策树时的参数
    'max_depth': scope.addfun(hp.randint('max_depth', 20), 5)
}

param_space_clf_adaboost_non_tree = {
    'base_estimator': hp.choice(
        'base_estimator', [
            SVC(),
            LogisticRegression(**{'C': 0.5848532840612014, 'class_weight': 'balanced', 'n_jobs': -1, 'penalty': 'l2'})
        ]
    ),
    'n_estimators': scope.addfun(hp.randint('n_estimators', 60), 30),
    'learning_rate': hp.loguniform('learning_rate', np.log(0.05), np.log(5))
}

###########best param###########
best_param_clf_lr = {
    'C': 0.07212442211840354,
    'class_weight': 'balanced',
    'n_jobs': -1,
    'penalty': 'l2'
}

best_param_clf_mlp = {
    'activation': 'relu',
    'alpha': 9.756090506594905e-05,
    'hidden_layer_sizes': (16, 32, 8),
    'learning_rate': 'adaptive',
    'learning_rate_init': 0.0703114914234283,
    'momentum': 0.1669382592981298, 'solver': 'sgd'
}

best_param_clf_xgboost = {
    'booster': 'gbtree',
    'colsample_bytree': 0.8,
    'eta': 0.19,
    'eval_metric': 'auc',
    'lambda': 2.2,
    'max_depth': 32,
    'n_estimators': 100.0,
    'nthread': -1,
    'objective': 'binary:logistic',
    'scale_pos_weight': 1,
    'subsample': 1
}

best_param_clf_xgboost_rise_down_zero = {
    'booster': 'gbtree',
    'colsample_bytree': 0.6000000000000001,
    'eta': 0.39,
    'eval_metric': 'auc',
    'lambda': 2.3000000000000003,
    'max_depth': 34,
    'n_estimators': 330.0,
    'nthread': -1,
    'objective': 'binary:logistic',
    'scale_pos_weight': 1,
    'subsample': 1.0
}

model_choice = \
    {
        'xgb': [XGBModel, param_space_clf_xgboost],
        'lr': [RollingLRModel, param_space_clf_lr],
        'svm': [SVM, param_space_clf_svm],
        'rf': [RFModel, param_space_clf_rf],
        'gbdt': [GBDTModel, param_space_clf_gbdt],
        'mlp': [MLPModel, param_space_clf_mlp],
        'adaboost_tree': [AdaBoostModelTree, param_space_clf_adaboost_tree],
        'adaboost_non_tree': [AdaBoostModelNonTree, param_space_clf_adaboost_non_tree]
    }
