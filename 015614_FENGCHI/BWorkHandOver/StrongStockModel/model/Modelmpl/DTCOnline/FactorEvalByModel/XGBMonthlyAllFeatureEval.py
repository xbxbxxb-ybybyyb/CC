# @Time : 2021/6/22 8:55
# @Author : Zhichen Lu
# @File : XGBMonthly.py

# @Time : 2020/9/17 9:22
# @Author : Zhichen Lu
# @File : train_XGBRegression.py
import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import numpy as np
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date
import pandas as pd
import xgboost as xgb
import os, gc, time, datetime, random
from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes

os.environ['CUDA_VISIBLE_DEVICES'] = '-1'
params = {'booster': 'gbtree', 'colsample_bytree': 0.8, 'eta': 0.1, 'gamma': 0.17761168444070607, 'max_depth': 16, 'min_child_weight': 1551, 'n_estimators': 100,
          'sampling_method': 'gradient_based', 'subsample': 0.8, 'tree_method': 'gpu_hist',
          'val_pred_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_val_pred/',
          'model_conf_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_model_conf/',
          'feature_path': '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_factor_list/',
          'load local model': True}


def eval_feature(factor_name, end_date=None):
    # pd.to_pickle([params,end_date],'/data/user/015664_old/param_for_feature_eval.pkl')
    # params,end_date = pd.read_pickle('/data/user/015664_old/param_for_feature_eval.pkl')
    if os.path.exists(f'{TARGET_PATH}/{end_date}/{factor_name}.npy'):
        print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f'|{factor_name}|{end_date} exist')
        return
    e = time.time()
    key_list = set(params.keys()).intersection(
        set(['booster', 'colsample_bytree', 'gamma', 'max_depth', 'min_child_weight', 'n_estimators', 'sampling_method', 'subsample', 'tree_method']))
    args_param = {x: params[x] for x in key_list}

    if 'load local model' in params and os.path.exists(params['model_conf_path'] + '%d.json' % end_date):
        model = xgb.Booster(args_param)
        model.load_model(params['model_conf_path'] + '%d.json' % end_date)
        model.set_param('predictor', 'cpu_predictor')
        print('load from local', end_date)
        # return model
    else:
        raise Exception('No Model Exist')
    model.set_param('predictor', 'cpu_predictor')
    val_features, _ = pd.read_pickle(params['val_pred_path'] + '%d.pkl' % end_date)
    idx = val_features.columns.tolist().index(factor_name)
    val_arr = val_features.values
    del val_features
    gc.collect()
    # d_val = xgb.DMatrix(val_features, label=val_labels['actual_label'])
    random.shuffle(val_arr[:, idx])
    d_val = xgb.DMatrix(val_arr)
    del val_arr
    gc.collect()
    factor_shuffle_arr = model.predict(d_val)
    del d_val
    gc.collect()
    if not os.path.exists(f'{TARGET_PATH}/{end_date}/'):
        os.makedirs(f'{TARGET_PATH}/{end_date}/')
    np.save(f'{TARGET_PATH}/{end_date}/{factor_name}.npy', factor_shuffle_arr.astype('float32'))
    total = time.time() - e
    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + f'|{factor_name}|{end_date} done with {total}')


TARGET_PATH = '/data/group/800442/800319/Faamonitor/PL/all_mkt_ts_norm/AllFeatureSelect/XGBAllFeature_AllFactor_train200_test10_EvalRes/'
if not os.path.exists(TARGET_PATH):
    os.makedirs(TARGET_PATH)

if __name__ == '__main__':

    docker_para = eval(aimr_multitimes.getParam())
    now = datetime.datetime.now()
    HHMM = int(now.strftime('%H%M'))
    no_running_period = [(610, 930), (1555, 1930)]
    forbiden_period = False
    for s, e in no_running_period:
        if HHMM > s and HHMM < e:
            forbiden_period = True
            break
    trading_day = get_recent_trade_date(int(now.strftime('%Y%m%d'))) == int(now.strftime('%Y%m%d'))

    if forbiden_period and trading_day:
        print('-----------forbidden period stop-----------------')
        pass
    else:
        eval_feature(*docker_para)
