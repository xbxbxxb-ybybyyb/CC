import sys
sys.path.append('/data/group/800442/800319/AWorkHandOver/alphaResearch/dataUpdate/')
sys.path.append('/data/group/800442/800319/')

import time
import os

import numpy as np
import pandas as pd
import xgboost as xgb
import lightgbm as lgb
import catboost as cb

from HANXU.Timing.StrategyTest import \
    load_timing_factor, load_timing_factor_test, wf1d1000, calc_test_months, \
    calc_start_date, calc_end_date, date_list, d2_move_max, d2_move_min
from dataApi.tradeDate import get_date_range, get_pre_trade_date


def timing_feature_engineering(X, y, d, t):
    X = X.reshape(X.shape[0], -1).T
    y = y.flatten()
    d = d.flatten()
    t = t.flatten()
    valid = (np.isfinite(X).sum(axis=1) > 0.8 * X.shape[1]) & np.isfinite(y)
    valid_samples = valid.sum()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
        valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))
    X = X[valid]
    y = y[valid]
    d = d[valid]
    t = t[valid]
    X[~ np.isfinite(X)] = 0
    return X, y, d, t


def timing_simple_model(X_train, y_train, d_train, t_train, X_test, y_test,
                        d_test, t_test, X_pred, d_pred, t_pred, long=True):
    X = np.r_[X_train, X_test, X_pred]
    d = np.r_[d_train, d_test, d_pred]
    t = np.r_[t_train, t_test, t_pred]
    arr = [pd.Series(X[:, x], index=[d, t]).unstack().values for x in range(X.shape[1])]
    move_func = d2_move_max if long else d2_move_min
    arr = [move_func(x, 40, 0.1) for x in arr]
    arr = np.asanyarray(arr).mean(axis=0)
    test_days = len(get_date_range(d_test[0], d_test[-1]))
    pred_days = len(get_date_range(d_pred[0], d_pred[-1]))
    pred = pd.DataFrame(arr[- pred_days:], index=get_date_range(d_pred[0], d_pred[-1]),
                        columns=[1000, 1030, 1100, 1300, 1330, 1400, 1430]).stack().reindex(
        pd.MultiIndex.from_arrays([d_pred, t_pred])).values
    test = pd.DataFrame(arr[- pred_days - test_days: - pred_days], index=get_date_range(d_test[0], d_test[-1]),
                        columns=[1000, 1030, 1100, 1300, 1330, 1400, 1430]).stack().reindex(
        pd.MultiIndex.from_arrays([d_test, t_test])).values
    return test, pred


def timing_xgb_model(X_train, y_train, d_train, t_train, X_test, y_test,
                     d_test, t_test, X_pred, d_pred, t_pred, long=True):
    config = dict(
        process_type='default',
        boooster='gbtree',
        objective='reg:linear',
        silent=False,
        nthread=-1,
        tree_method='gpu_hist',
        # tree_method='hist',
        eta=0.15,
        # num_boost_round=20,
        max_depth=4,
        min_child_weight=50,
        gamma=0,
        subsample=1,
        colsample_bytree=1,
        # reg_alpha=0,
        reg_lambda=0,
        scale_pos_weight=1,
        max_delta_step=0,
        num_boost_round=1000,
        xgb_model=None
    )
    train = xgb.DMatrix(X_train, label=y_train)
    test = xgb.DMatrix(X_test, label=y_test)
    model = xgb.train(config, train, num_boost_round=config['num_boost_round'],
                      early_stopping_rounds=15, evals=[(train, 'train'), (test, 'test')],
                      verbose_eval=True)
    yh_test = model.predict(xgb.DMatrix(X_test)).flatten()
    yh_pred = model.predict(xgb.DMatrix(X_pred)).flatten()
    return yh_test, yh_pred


def timing_lgb_model(X_train, y_train, d_train, t_train, X_test, y_test,
                     d_test, t_test, X_pred, d_pred, t_pred, long=True):
    config = dict(
        boosting_type='gbdt',
        num_leaves=31,
        max_depth=5,
        learning_rate=0.1,
        n_estimators=100,
        subsample=1.,
        subsample_freq=0,
        colsample_bytree=1.,
        reg_alpha=0.,
        reg_lambda=0.,
        random_state=None,
        n_jobs=-1,
        silent=True,
        importance_type='split'
    )
    train = lgb.Dataset(X_train, label=y_train)
    test = lgb.Dataset(X_test, label=y_test)
    model = lgb.LGBMRegressor(config)
    model.fit(X_train, y_train, eval_set=[train, test], eval_names=['train', 'test'], early_stopping_rounds=50)
    y_test = model.predict(X_test)
    y_pred = model.predict(X_pred)
    return y_test, y_pred


def timing_cat_model(X_train, y_train, d_train, t_train, X_test, y_test,
                     d_test, t_test, X_pred, d_pred, t_pred, long=True):
    config = dict(
        learning_rate=0.05,
        loss_function='Logloss',
        eval_metric='Accuracy',
        depth=6,
        min_data_in_leaf=20,
        random_seed=42,
        logging_level='Silent',
        use_best_model=True,
        one_hot_max_size=5,
        boosting_type='Ordered',
        max_ctr_complexity=2,
        nan_mode='Min'
    )

    pool_test = cb.Pool(data=X_test, label=y_test)
    model = cb.CatBoostRegressor(early_stopping_rounds=50, **config)
    model.fit(X_train, eval_set=pool_test, plot=True)
    y_test = model.predict(X_test)
    y_pred = model.predict(X_pred)
    return y_test, y_pred


select_num = 300
signal_name = 'XGB300'
model_func = timing_xgb_model

select_address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/'
all_model_month = calc_test_months('M')
model_month = calc_test_months('M', start=201609, end=202111)

long_dic = {}
short_dic = {}
long_pred = {}
short_pred = {}
for mh in model_month:
    test_end = calc_end_date(mh)
    test_start = get_pre_trade_date(test_end, 38)
    train_end = get_pre_trade_date(test_start, 2)
    train_start = calc_start_date(mh, 36)
    pred_start = get_pre_trade_date(test_end, -2)
    pred_end = min(get_pre_trade_date(calc_end_date(all_model_month[all_model_month.index(mh) + 1]), -1), date_list[-1])

    if os.path.exists(f'{select_address}/MixFactor/{mh}_long.pkl'):
        long_list = pd.read_pickle(f'{select_address}/MixFactor/{mh}_long.pkl')
    else:
        os.makedirs(f'{select_address}/MixFactor/', exist_ok=True)
        long_list = pd.read_pickle(f'{select_address}/MixFactorLong.pkl').index
        long_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in long_list}).T
        long_list['mix_IC'] = long_list['IC'] + long_list['多头IC']
        long_list['mix_mdd'] = long_list['回撤期多头占比'] / long_list['多头占比'] * long_list['回撤期多头年化']
        long_list['score'] = long_list['mix_IC'].rank() + long_list['mix_mdd'].rank()
        long_list = long_list.sort_values('score', ascending=False).head(select_num)
        pd.to_pickle(long_list, f'{select_address}/MixFactor/{mh}_long.pkl')
        print(f'已保存至{select_address}/MixFactor/{mh}_long.pkl')

    X = np.r_['0,3', tuple(load_timing_factor(x) * long_list.loc[x, '因子方向'] for x in long_list.index)]

    X_train = X[:, date_list.index(train_start): date_list.index(train_end) + 1]
    X_test = X[:, date_list.index(test_start): date_list.index(test_end) + 1]
    X_pred = X[:, date_list.index(pred_start): date_list.index(pred_end) + 1]

    y_train = wf1d1000[date_list.index(train_start): date_list.index(train_end) + 1]
    y_test = wf1d1000[date_list.index(test_start): date_list.index(test_end) + 1]
    y_pred = wf1d1000[date_list.index(pred_start): date_list.index(pred_end) + 1]

    d_train = np.asanyarray(get_date_range(train_start, train_end))[:, None].repeat(7, axis=1)
    d_test = np.asanyarray(get_date_range(test_start, test_end))[:, None].repeat(7, axis=1)
    d_pred = np.asanyarray(get_date_range(pred_start, pred_end))[:, None].repeat(7, axis=1)

    t_train = np.asanyarray([1000, 1030, 1100, 1300, 1330, 1400, 1430])[None, :].repeat(d_train.shape[0], axis=0)
    t_test = np.asanyarray([1000, 1030, 1100, 1300, 1330, 1400, 1430])[None, :].repeat(d_test.shape[0], axis=0)
    t_pred = np.asanyarray([1000, 1030, 1100, 1300, 1330, 1400, 1430])[None, :].repeat(d_pred.shape[0], axis=0)

    X_train, y_train, d_train, t_train = timing_feature_engineering(X_train, y_train, d_train, t_train)
    X_test, y_test, d_test, t_test = timing_feature_engineering(X_test, y_test, d_test, t_test)
    X_pred, y_pred, d_pred, t_pred = timing_feature_engineering(X_pred, y_pred, d_pred, t_pred)

    yh1_test, yh1_pred = model_func(X_train, y_train, d_train, t_train, X_test, y_test,
                                          d_test, t_test, X_pred, d_pred, t_pred, long=True)

    h1_test = pd.DataFrame({'d': d_test, 't': t_test, 'yh': yh1_test}).set_index(['d', 't']).unstack()
    h1_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': yh1_pred}).set_index(['d', 't']).unstack()
    h1 = pd.concat([h1_test, h1_pred])
    h1 = pd.DataFrame(d2_move_max(h1.values, 40, 0.3), index=h1.index[39:], columns=h1.columns).reindex(h1_pred.index)
    long_dic[mh] = h1
    long_pred[mh] = h1_pred

    if os.path.exists(f'{select_address}/MixFactor/{mh}_short.pkl'):
        short_list = pd.read_pickle(f'{select_address}/MixFactor/{mh}_short.pkl')
    else:
        os.makedirs(f'{select_address}/MixFactor/', exist_ok=True)
        short_list = pd.read_pickle(f'{select_address}/MixFactorShort.pkl').index
        short_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in short_list}).T
        short_list['mix_IC'] = short_list['IC'] + short_list['空头IC']
        short_list['mix_mdd'] = short_list['空头占比'] / short_list['回撤期空头占比'] * short_list['回撤期空头年化']
        short_list['score'] = short_list['mix_IC'].rank() + short_list['mix_mdd'].rank()
        short_list = short_list.sort_values('score', ascending=False).head(select_num)
        pd.to_pickle(short_list, f'{select_address}/MixFactor/{mh}_short.pkl')
        print(f'已保存至{select_address}/MixFactor/{mh}_short.pkl')

    X = np.r_['0,3', tuple(load_timing_factor(x) * short_list.loc[x, '因子方向'] for x in short_list.index)]

    X_train = X[:, date_list.index(train_start): date_list.index(train_end) + 1]
    X_test = X[:, date_list.index(test_start): date_list.index(test_end) + 1]
    X_pred = X[:, date_list.index(pred_start): date_list.index(pred_end) + 1]

    y_train = wf1d1000[date_list.index(train_start): date_list.index(train_end) + 1]
    y_test = wf1d1000[date_list.index(test_start): date_list.index(test_end) + 1]
    y_pred = wf1d1000[date_list.index(pred_start): date_list.index(pred_end) + 1]

    d_train = np.asanyarray(get_date_range(train_start, train_end))[:, None].repeat(7, axis=1)
    d_test = np.asanyarray(get_date_range(test_start, test_end))[:, None].repeat(7, axis=1)
    d_pred = np.asanyarray(get_date_range(pred_start, pred_end))[:, None].repeat(7, axis=1)

    t_train = np.asanyarray([1000, 1030, 1100, 1300, 1330, 1400, 1430])[None, :].repeat(d_train.shape[0], axis=0)
    t_test = np.asanyarray([1000, 1030, 1100, 1300, 1330, 1400, 1430])[None, :].repeat(d_test.shape[0], axis=0)
    t_pred = np.asanyarray([1000, 1030, 1100, 1300, 1330, 1400, 1430])[None, :].repeat(d_pred.shape[0], axis=0)

    X_train, y_train, d_train, t_train = timing_feature_engineering(X_train, y_train, d_train, t_train)
    X_test, y_test, d_test, t_test = timing_feature_engineering(X_test, y_test, d_test, t_test)
    X_pred, y_pred, d_pred, t_pred = timing_feature_engineering(X_pred, y_pred, d_pred, t_pred)

    yh2_test, yh2_pred = model_func(X_train, y_train, d_train, t_train, X_test, y_test,
                                          d_test, t_test, X_pred, d_pred, t_pred, long=False)

    h2_test = pd.DataFrame({'d': d_test, 't': t_test, 'yh': yh2_test}).set_index(['d', 't']).unstack()
    h2_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': yh2_pred}).set_index(['d', 't']).unstack()
    h2 = pd.concat([h2_test, h2_pred])
    h2 = pd.DataFrame(d2_move_min(h2.values, 40, 0.3), index=h2.index[39:], columns=h2.columns).reindex(h2_pred.index)
    short_dic[mh] = h2
    short_pred[mh] = h2_pred

long_df = pd.concat([long_dic[x] for x in model_month])
short_df = pd.concat([short_dic[x] for x in model_month])
long_pred = pd.concat([long_pred[x] for x in model_month])
short_pred = pd.concat([short_pred[x] for x in model_month])
signal = ((long_df > 0) & (short_df == 0)).astype('float64') - short_df.astype('float64')
signal.to_pickle(f'/data/group/800442/800319/Timing/BackTest/Signal/{signal_name}.pkl')
long_pred.to_pickle(f'/data/group/800442/800319/Timing/BackTest/Signal/long_pred_{signal_name}.pkl')
short_pred.to_pickle(f'/data/group/800442/800319/Timing/BackTest/Signal/short_pred_{signal_name}.pkl')


# long_pred = pd.read_pickle(f'/data/group/800442/800319/Timing/BackTest/Signal/long_pred_XGB300.pkl')
# real_y = pd.DataFrame(wf1d1000[-1238:], index=long_pred.index, columns=long_pred.columns).stack().reset_index()
# long_pred = long_pred.stack().reset_index()
# df = pd.concat([long_pred, real_y['yh'].rename('ry')], axis=1)
# df['m'] = df['d'] // 100
# df_corr = df.groupby('m').apply(lambda x: x['yh'].corr(x['ry']))
# ry_des = df.groupby('m')['ry'].describe()
# yh_des = df.groupby('m')['yh'].describe()
