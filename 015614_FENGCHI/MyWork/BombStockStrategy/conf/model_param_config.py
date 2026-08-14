# coding: utf-8
# Author：fengchi863
# Date ：2021/11/2 14:38


###### bset model param ######
best_param_clf_lr = {
    'C': 0.05500036818661201,
    'class_weight': 'balanced',
    'n_jobs': -1,
    'penalty': 'l2'
}

best_param_clf_xgb = {
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

best_param_clf_lgb = {
    'max_depth': 5,
    'lambda': 2.2,
    'bagging_fraction': 0.95,
    'early_stopping_round': 30,
    'num_leaves': 8, # < 2 * max_depth
    'min_data_in_leaf': 1000,
    'min_bin': 50,
    'learning_rate': 0.03
}