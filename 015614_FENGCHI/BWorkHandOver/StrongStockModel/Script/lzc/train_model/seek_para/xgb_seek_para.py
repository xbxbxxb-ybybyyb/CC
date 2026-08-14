# @Time : 2021/1/22 10:47
# @Author : Zhichen Lu
# @File : xgb_seek_para.py
import xgboost as xgb
import pandas as pd
from hyperopt import fmin,hp,tpe,rand
import random
import os
import logging,gc

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("/data/user/015664/AFuckingTrigger/seek_para/xgb/tree_param_depth_child_weight_searching.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

def train_one_param(param):
    idx = random.sample(list(range(1000)), 1)[0]
    print(param)
    while os.path.exists(f'/data/user/015664/AFuckingTrigger/seek_para/xgb/searching_result/{idx}.pkl'):
        idx = random.sample(list(range(1000)), 1)[0]
    X_train, y_train, X_test, y_test = pd.read_pickle('/data/user/015664/AFuckingTrigger/seek_para/xgb27.pkl')
    d_train = xgb.DMatrix(X_train[:-200000],label=y_train[:-200000].values)
    d_eval = xgb.DMatrix(X_train[-200000:],label=y_train[-200000:].values)
    d_test = xgb.DMatrix(X_test)
    model = xgb.train(param,d_train,num_boost_round=param['n_estimators'],evals=[(d_eval,'d_eval')],early_stopping_rounds=15,verbose_eval=False)
    y_test['prediction'] = model.predict(d_test)

    corr,mae  = y_test.corr().values[0, 1], abs(y_test['actual_label'] - y_test['prediction']).mean()
    logger.info(str(param))
    logger.info(f'corr:{corr}    mae:{mae}')
    logger.info('***********************************************')
    pd.to_pickle({'para': param, 'res': y_test,'corr':corr,'mae':mae}, f'/data/user/015664/AFuckingTrigger/seek_para/xgb/searching_result/{idx}.pkl')
    return 1-corr

def train_wrpaer(param):
    res = train_one_param(param)
    gc.collect()
    return res


logger.info('--------------------------hyperparamopt start-------------------------------------')

hyper_space_xgb_stage1 = {
    'booster': 'gbtree',
    'eta':hp.uniform('colsample_bytree',0.1,0.8),
    'colsample_bytree': 0.8,#hp.uniform('colsample_bytree',0.5,0.9),
    'max_depth': 5,
    'subsample': 0.8,#hp.uniform('subsample',0.5,1),
    'gamma':0,#hp.uniform('gamma',0,0.2),
    'min_child_weight':1,
    'tree_method': 'gpu_hist',
    'sampling_method': 'gradient_based',
    'n_estimators': 200
}

hyper_space_xgb_stage2 = {
    'booster': 'gbtree',
    'eta':0.1,
    'colsample_bytree': hp.uniform('colsample_bytree',0.5,0.9),
    'max_depth': 16,
    'subsample': hp.uniform('subsample',0.5,1),
    'gamma':0.17761168444070607,#hp.uniform('gamma',0,0.2),
    'min_child_weight':1551,
    'tree_method': 'gpu_hist',
    'sampling_method': 'gradient_based',
    'n_estimators': 100
}
# train_wrpaer({'booster': 'gbtree', 'colsample_bytree': 0.5198894235327541, 'gamma': 0.17142211783639102, 'max_depth': 4, 'min_child_weight': 7530, 'n_estimators': 100, 'sampling_method': 'gradient_based', 'subsample': 0.7022893137593411, 'tree_method': 'gpu_hist'})
best = fmin(train_wrpaer, hyper_space_xgb_stage1, algo=tpe.suggest, max_evals=200)

logger.info(f'best: {best}')