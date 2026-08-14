# @Time : 2022/4/27 14:10
# @Author : Zhichen Lu
# @File : param_seeking.py

# @Time : 2022/4/16 18:43
# @Author : Zhichen Lu
# @File : param_opt.py
# @Time : 2021/1/22 10:47
# @Author : Zhichen Lu
# @File : xgb_seek_para.py
import sys

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(
    ['/data/user/015664/TriggeredTrading', '/data/user/015664/TriggeredTrading/FeatureEngineering', '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python',
     '/data/user/015664/TriggeredTrading/StrongStockModel',
     '/data/user/015664/TriggeredTrading/Deep-Reinforcement-Learning-for-Automated-Stock-Trading-Ensemble-Strategy-ICAIF-2020-master',
     '/data/user/015664/TriggeredTrading/FactorAlpha', '/data/user/015664/TriggeredTrading/CrossFT', '/data/user/015664/TriggeredTrading/CrossFT/basic',
     '/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/FactorCalculator_', '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/training',
     '/data/user/015664/TriggeredTrading/Temporal_Relational_Stock_Ranking-master/preprocess', '/data/user/015664/TriggeredTrading/StockSelection',
     '/data/user/015664/TriggeredTrading'])

import xgboost as xgb
import os
import pandas as pd
import numpy as np
import gc
from tqdm import tqdm
from hyperopt import fmin, hp, tpe, rand
from sklearn.model_selection import KFold
from sklearn import metrics
import logging, gc

ind_name = 'ic_t'
base_dir = f'/data/user/015664/AFuckingTrigger/ParamSeeking/XGB20220427/{ind_name}/'

logger = logging.getLogger(__name__)
logger.setLevel(level=logging.INFO)
handler = logging.FileHandler(f"{base_dir}/param.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

X_train, y_train, X_test, y_test = pd.read_pickle(f'{base_dir}/{ind_name}_20170101_20171231.pkl')
boost_round = 200
val_num = 500000
d_train = xgb.DMatrix(X_train.iloc[:-val_num], label=y_train['actual_label'].iloc[:-val_num])
d_val = xgb.DMatrix(X_train.iloc[-val_num:], label=y_train['actual_label'].iloc[-val_num:])
d_test = xgb.DMatrix(X_test, label=y_test['actual_label'])


def pred_val(param):
    print(param)
    model = xgb.train(param, d_train, num_boost_round=boost_round, evals=[(d_val, 'd_val')], early_stopping_rounds=10, verbose_eval=True)
    model.set_param('predictor', 'cpu_predictor')
    bst_iteration = model.best_iteration
    res = pd.DataFrame({'label': y_test['actual_label'], 'prediction': model.predict(d_test)})
    ic = res.corr().iloc[0, 1]
    mae = abs(res['label'] - res['prediction']).mean()
    logger.info(str(param))
    logger.info(f'corr:{ic}    mae:{mae} iteration {bst_iteration}')
    logger.info('------------')

    return 1 - ic


def train_wrpaer(param):
    res = pred_val(param)
    gc.collect()
    return res


hyper_space_xgb_stage1 = {
    'booster': 'gbtree',
    'eta': hp.uniform('eta', 0.1, 0.8),
    'colsample_bytree': 0.8,  # hp.uniform('colsample_bytree',0.5,0.9),
    'max_depth': 5,
    'subsample': 0.8,  # hp.uniform('subsample',0.5,1),
    'gamma': 0,  # hp.uniform('gamma',0,0.2),
    'min_child_weight': 1,
    'tree_method': 'gpu_hist',
    'sampling_method': 'gradient_based',
    'n_estimators': 200
}
# 第一步 寻优学习率
best1 = fmin(train_wrpaer, hyper_space_xgb_stage1, algo=tpe.suggest, max_evals=100)
print('-------------')
print(best1)
logger.info(f'best stage1 {best1}')
logger.info('****************************************************************')
hyper_space_xgb_stage2 = hyper_space_xgb_stage1.copy()
hyper_space_xgb_stage2.update(best1)

pd.to_pickle(hyper_space_xgb_stage2, f'{base_dir}/best1.pkl')
logger.info(f'best stage1 all {hyper_space_xgb_stage2}')

hyper_space_xgb_stage2 = pd.read_pickle(f'{base_dir}/best1.pkl')

hyper_space_xgb_stage2.update({
    'max_depth': hp.choice('max_depth', list(range(3, 10))),
    'min_child_weight': hp.choice('min_child_weight', list(range(1, 6))),
})
# 第二步 寻优 maxdepth,min_child_weight
best2 = fmin(train_wrpaer, hyper_space_xgb_stage2, algo=tpe.suggest, max_evals=40)
best2 = {
    'max_depth': list(range(3, 10))[best2['max_depth']],
    'min_child_weight': list(range(1, 6))[best2['min_child_weight']],
}
print(f'best2 {best2}')
logger.info(f'best stage2 {best2}')
logger.info('****************************************************************')
hyper_space_xgb_stage3 = hyper_space_xgb_stage2.copy()
hyper_space_xgb_stage3.update(best2)
pd.to_pickle(hyper_space_xgb_stage3, f'{base_dir}/best2.pkl')
logger.info(f'best stage2 all {hyper_space_xgb_stage3}')

hyper_space_xgb_stage3.update({
    'gamma': hp.uniform('gamma', 0, 0.2)
})
# 第三步 寻优gamma
best3 = fmin(train_wrpaer, hyper_space_xgb_stage3, algo=tpe.suggest, max_evals=30)
print(f'best 3 {best3}')

hyper_space_xgb_stage4 = hyper_space_xgb_stage3.copy()
hyper_space_xgb_stage4.update(best3)
pd.to_pickle(hyper_space_xgb_stage4, f'{base_dir}/best3.pkl')
logger.info(f'best stage3 {best3}')
logger.info('****************************************************************')
logger.info(f'best stage3 all {hyper_space_xgb_stage4}')

# hyper_space_xgb_stage4 = pd.read_pickle(f'{base_dir}/best3.pkl')
hyper_space_xgb_stage4.update({
    'subsample': hp.uniform('subsample', 0.5, 1),
    'colsample_bytree': hp.uniform('colsample_bytree', 0.5, 1)
})
# 第四步 寻优 样本、特征采样比例
best4 = fmin(train_wrpaer, hyper_space_xgb_stage4, algo=tpe.suggest, max_evals=200)

print('stage4', best4)

hyper_space_xgb_stage5 = hyper_space_xgb_stage4.copy()
hyper_space_xgb_stage5.update(best4)
pd.to_pickle(hyper_space_xgb_stage5, f'{base_dir}/best4.pkl')
logger.info(f'best stage4 {best4}')
logger.info('****************************************************************')
logger.info(f'best stage4 all {hyper_space_xgb_stage5}')
hyper_space_xgb_stage5.update({
    'reg_alpha': hp.choice('reg_alpha', [1e-5, 1e-4, 1e-3, 1e-2, 0.1, 1, 100])
})
# 第五步 正则化寻优
best5 = fmin(train_wrpaer, hyper_space_xgb_stage5, algo=tpe.suggest, max_evals=10)

best5 = {
    'reg_alpha': [1e-5, 1e-4, 1e-3, 1e-2, 0.1, 1, 100][best5['reg_alpha']]
}
hyper_space_xgb_stage5.update(best5)
pd.to_pickle(hyper_space_xgb_stage5, f'{base_dir}/best5.pkl')
logger.info(f'best stage5 {best5}')
logger.info('****************************************************************')
logger.info(f'best stage5 all {hyper_space_xgb_stage5}')
check = pd.read_pickle(f'{base_dir}/best5.pkl')
# check