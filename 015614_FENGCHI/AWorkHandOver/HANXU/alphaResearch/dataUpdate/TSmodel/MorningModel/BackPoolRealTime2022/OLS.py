import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.MorningModelDataPrepare import \
    morning_data_prepare7, feature_engineering, factor_engineering, morning_factor_prepare7
from TSmodel.MorningModel.Tree import prepare_model_fold
from TSmodel.MorningModel.AlgoCSResearch.FactorSelect.factor_select import *
import pandas as pd
from dataApi import aimr
import xgboost as xgb
import torch
import time
import gc
import os

def set_model():
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    return model


def train_model(X_train, y_train, d_train, c_train, ry_train, model, model_name, model_root, model_idx):
    model.fit(X_train, y_train)
    from sklearn.externals import joblib
    joblib.dump(model, f'{model_root}/{model_name}/conf/{model_idx}.pkl')
    yh_train = model.predict(X_train)
    df_train = pd.DataFrame({'date': d_train, 'code': c_train, 'ry': ry_train, 'y': y_train, 'yh': yh_train})
    df_train.to_pickle(f'{model_root}/{model_name}/train/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model


def pred_model(X, d, c, model, model_name, model_root, model_idx, pred_type='pred'):
    yh = model.predict(X)
    df_pred = pd.DataFrame({'date': d, 'code': c, 'yh': yh})
    df_pred.to_pickle(f'{model_root}/{model_name}/{pred_type}/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish {pred_type} model {model_idx}')
    return df_pred

def _infer_str(param):
    infer = param.split('|')
    infer[0] = eval(infer[0])
    infer[1] = eval(infer[1]) if '[' in infer[1] else infer[1]
    infer[3] = int(infer[3])
    infer[4] = float(infer[4])
    infer[5] = eval(infer[5])
    return infer

def train_ols(model_gen, date=None):

    pred_end = date if date else get_recent_trade_date()
    pred_start = pred_end
    train_end = get_pre_trade_date(pred_start, 6)
    train_start = get_pre_trade_date(train_end, 487)


    model_name = 'OLS_' + model_gen
    model_root = '/arch1/user/015836/HFmodel/AlgoCSResearch/RealTime20220104/'
    prepare_model_fold(model_name, model_root)
    if os.path.exists(f'{model_root}/{model_name}/pred/{pred_end}.pkl'):
        return pd.read_pickle(f'{model_root}/{model_name}/pred/{pred_end}.pkl')

    future_type = 'future930t30h135d'
    future_std = 'future_uniform20t50'

    factor_list = done_select(train_start, train_end, *_infer_str(model_gen))

    X_train, y_train, ry_train, d_train, c_train = morning_data_prepare7(
        factor_list, train_start, train_end, future_type, future_std)
    X_train, y_train, ry_train, d_train, c_train = feature_engineering(
        X_train, y_train, ry_train, d_train, c_train)

    X_pred, d_pred, c_pred = morning_factor_prepare7(
        factor_list, pred_start, pred_end)
    X_pred, d_pred, c_pred = factor_engineering(
        X_pred, d_pred, c_pred)

    model = set_model()
    model = train_model(X_train, y_train, d_train, c_train, ry_train, model, model_name, model_root, pred_end)
    pred = pred_model(X_pred, d_pred, c_pred, model, model_name, model_root, pred_end, 'pred')
    torch.cuda.empty_cache()
    gc.collect()
    return pred

