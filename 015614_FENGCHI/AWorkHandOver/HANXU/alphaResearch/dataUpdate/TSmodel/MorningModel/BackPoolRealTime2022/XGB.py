import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.MorningModelDataPrepare import \
    morning_data_prepare7, feature_engineering, factor_engineering, morning_factor_prepare7
from TSmodel.MorningModel.Tree import prepare_model_fold
from TSmodel.MorningModel.AlgoCSResearch.FactorSelect.factor_select import *
import pandas as pd
import xgboost as xgb
import torch
import time
import gc
import os


def set_model():
    config = dict(
        process_type='default',
        boooster='gbtree',
        objective='reg:linear',
        silent=False,
        nthread=-1,
        tree_method='gpu_hist',
        eta=0.1,
        # num_boost_round=20,
        max_depth=6,
        min_child_weight=50,
        gamma=0,
        subsample=0.8,
        colsample_bytree=0.8,
        # reg_alpha=0,
        reg_lambda=0,
        scale_pos_weight=1,
        max_delta_step=0,
        num_boost_round=200,
        xgb_model=None
    )
    return config


def train_model(X_train, y_train, config, factor_list, model_name, model_root, model_idx):
    X_train = xgb.DMatrix(X_train, label=y_train)
    model = xgb.train(config, X_train, num_boost_round=config['num_boost_round'])
    score = pd.DataFrame([pd.Series(model.get_score(importance_type=x)).rename(x) for x in [
        'weight', 'gain', 'cover', 'total_gain', 'total_cover']]).T
    score.index = score.index.map(lambda x: int(x[1:]))
    score = score.sort_index().reindex(range(len(factor_list))).fillna(0)
    score.index = factor_list
    score.to_pickle(f'{model_root}/{model_name}/score/{model_idx}.pkl')
    model.save_model(f'{model_root}/{model_name}/conf/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish train model {model_idx}')
    return model


def pred_model(X, d, c, model, model_name, model_root, model_idx, pred_type='pred'):
    yh = model.predict(xgb.DMatrix(X)).flatten()
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


def train_xgb(model_gen, date=None):
    model_name = 'XGB200_' + model_gen
    model_root = '/arch1/user/015836/HFmodel/AlgoCSResearch/RealTime20220104/'
    prepare_model_fold(model_name, model_root)
    pred_end = date if date else get_recent_trade_date()
    pred_start = pred_end
    train_end = get_pre_trade_date(pred_start, 6)
    train_start = get_pre_trade_date(train_end, 487)

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

    config = set_model()
    model = train_model(X_train, y_train, config, factor_list, model_name, model_root, pred_end)
    pred = pred_model(X_pred, d_pred, c_pred, model, model_name, model_root, pred_end, 'pred')
    torch.cuda.empty_cache()
    gc.collect()
    return pred


def pred_xgb(model_gen, date=None):
    model_name = 'XGB200_' + model_gen
    model_root = '/arch1/user/015836/HFmodel/AlgoCSResearch/RealTime20220104/'
    pred_end = date if date else get_recent_trade_date()
    pred_start = pred_end

    model_end = sorted([int(x[:-4]) for x in os.listdir(f'{model_root}/{model_name}/conf/')
                        if int(x[:-4]) <= pred_end])[-1]
    train_end = get_pre_trade_date(model_end, 6)
    train_start = get_pre_trade_date(train_end, 487)
    factor_list = done_select(train_start, train_end, *_infer_str(model_gen))

    X_pred, d_pred, c_pred = morning_factor_prepare7(factor_list, pred_start, pred_end)
    X_pred, d_pred, c_pred = factor_engineering(X_pred, d_pred, c_pred)
    model = xgb.Booster(model_file=f'{model_root}/{model_name}/conf/{model_end}.pkl')
    model.set_param({'predictor': 'cpu_predictor'})
    pred = pred_model(X_pred, d_pred, c_pred, model, model_name, model_root, pred_end, 'pred')
    return pred
