import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

from TSmodel.MorningModel.MorningModelDataPrepare import \
    morning_data_prepare, feature_engineering, select_factor_list2, morning_factor_prepare, factor_engineering
from TSmodel.MorningModel.LR import prepare_model_fold, set_model, train_model, pred_model
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date
from dataApi.getData import get_daily_1factor
import pandas as pd
import numpy as np
import time
import gc
import os

def infer_code_list(date_list):

    address = '/data/group/800442/800319/HFfactor/MorningFactor/data/'
    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date
    code_list = sorted(list(set(idx_code[choose])))
    return code_list

def pred_y(X, d, c, model, model_name, model_root, model_idx, pred_type='pred'):

    yh = model.predict(X)
    df_pred = pd.DataFrame({'date': d, 'code': c, 'yh': yh})
    df_pred.to_pickle(f'{model_root}/{model_name}/{pred_type}/{model_idx}.pkl')
    print(time.strftime('%Y-%m-%d %H:%M:%S'), f'Finish {pred_type} model {model_idx}')
    return df_pred

pred_end = get_recent_trade_date()
pred_start = pred_end
train_end = get_pre_trade_date(pred_start, 2)
train_start = get_pre_trade_date(train_end, 244)

train_days = 244
predict_days = 1
corr_ignore = False
factor_num = 100
prefix = 'TS'
future_type = 'future930t30h1d'
future_days_max = 1
future_std = 'future'
statistics_address = '/data/group/800442/800319/HFfactor/MorningFactor/statistics/ts1d930_ic10ret_multi_summary_corr7/'
folds = 4
rho = 1

model_name = 'TS_OLS_F100T244P1_future930t30h1dq'
model_root = '/arch1/user/015836/HFmodel/MorningModel/LR/RealTime_ols_ts1d930q/'
prepare_model_fold(model_name, model_root)


for fold in range(folds):
    _model_name = f'TT{fold}_{model_name}'
    prepare_model_fold(_model_name, model_root)

    train_dates = get_date_range(train_start, train_end)

    code_list = get_daily_1factor('mkt_cap_ard', train_dates, infer_code_list(train_dates)).mean().sort_values()
    test_codes = sorted(code_list[fold::folds].index.to_list())
    train_codes = sorted(set(code_list.index) - set(test_codes))
    factor_list = select_factor_list2(train_end, factor_num, prefix, statistics_address)

    X_train, y_train, ry_train, d_train, c_train = morning_data_prepare(
        factor_list, train_start, train_end, future_type, future_std, True, train_codes)
    X_test, y_test, ry_test, d_test, c_test = morning_data_prepare(
        factor_list, train_start, train_end, future_type, future_std, True, test_codes)
    X_pred, d_pred, c_pred = morning_factor_prepare(factor_list, pred_start, pred_end, True)

    X_train, y_train, ry_train, d_train, c_train = feature_engineering(
        X_train, y_train, ry_train, d_train, c_train)
    X_test, y_test, ry_test, d_test, c_test = feature_engineering(
        X_test, y_test, ry_test, d_test, c_test)
    X_pred, d_pred, c_pred = factor_engineering(X_pred, d_pred, c_pred)

    model = set_model()
    model = train_model(X_train, y_train, d_train, c_train, ry_train,
                             model, _model_name, model_root, train_end)
    pred_model(X_test, y_test, d_test, c_test, ry_test,
               model, _model_name, model_root, pred_end, 'test')
    pred_y(X_pred, d_pred, c_pred, model, _model_name, model_root, pred_end, 'pred')
    gc.collect()


test = pd.concat([pd.read_pickle(f'{model_root}/TT{x}_{model_name}/test/{pred_end}.pkl') for x in range(folds)]
                 ).sort_values(['date', 'code'])
pred = pd.DataFrame({x: pd.read_pickle(f'{model_root}/TT{x}_{model_name}/pred/{pred_end}.pkl').set_index(
    ['date', 'code'])['yh'].rename(x) for x in range(folds)}).mean(axis=1).rename('yh').reset_index()

test_t_ic = test.groupby('code').apply(lambda x: x['y'].corr(x['yh'])).mean()

yh_mean = test.groupby('code')['yh'].mean()
yh_std = test.groupby('code')['yh'].std()
yh_pred = pred.groupby('code')['yh'].mean()

choose = (yh_pred > (yh_mean + rho * yh_std).reindex(yh_pred.index))
sign_num = choose.sum()
sign_pct = sign_num / len(choose)
result = [pred_end, sign_num, sign_pct, test_t_ic]
pd.to_pickle(result, '/data/group/800442/800319/strategy_local_path/market_timing/' + '%d.pkl' % pred_end)