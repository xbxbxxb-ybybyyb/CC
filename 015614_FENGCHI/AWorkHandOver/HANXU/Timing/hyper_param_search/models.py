# coding: utf-8
# Author：fengchi863
# Date ：2022/6/20 13:53

from HANXU.Timing.StrategyTest import \
    load_timing_factor, load_timing_factor_test, wf1d1000, calc_test_months, \
    calc_start_date, calc_end_date, date_list, d2_move_max, d2_move_min
from dataApi.tradeDate import get_date_range, get_pre_trade_date
import pandas as pd
import numpy as np
import xgboost as xgb
import random
import os
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout

random.seed(2022)

select_address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/NewSelect/'
all_model_month = calc_test_months('M')
model_month = calc_test_months('M', start=201609, end=202111)
# model_month = calc_test_months('M', start=202105, end=202111)

fflong_address = '/data/group/800442/800319/Timing/FixFactor/FixFactor/wyl/factor_pools/'


def timing_feature_engineering(X, y, d, t):
    X = X.reshape(X.shape[0], -1).T
    y = y.flatten()
    d = d.flatten()
    t = t.flatten()
    valid = (np.isfinite(X).sum(axis=1) > 0.7 * X.shape[1]) & np.isfinite(y)
    # valid_samples = valid.sum()
    # print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
    #     valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))
    X = X[valid]
    y = y[valid]
    d = d[valid]
    t = t[valid]
    X[~ np.isfinite(X)] = 0
    return X, y, d, t


def timing_xgb_model(X_train, y_train, d_train, t_train, X_test, y_test,
                     d_test, t_test, X_pred, d_pred, t_pred, config):
    train = xgb.DMatrix(X_train, label=y_train)
    test = xgb.DMatrix(X_test, label=y_test)
    model = xgb.train(config, train,
                      num_boost_round=config['num_boost_round'],
                      early_stopping_rounds=config['early_stopping_rounds'],
                      evals=[(train, 'train'), (test, 'test')],
                      verbose_eval=False)

    yh_test = model.predict(xgb.DMatrix(X_test)).flatten()
    yh_pred = model.predict(xgb.DMatrix(X_pred)).flatten()
    return yh_test, yh_pred


def timing_lstm_model(X_train, y_train, d_train, t_train, X_test, y_test,
                     d_test, t_test, X_pred, d_pred, t_pred, config):
    lstm_model = Sequential()
    lstm_model.add(LSTM(64, input_shape=(X_train.shape[1], X_train.shape[2])))
    lstm_model.add(Dropout(0.5))
    lstm_model.add(Dense(1, activation='relu'))
    lstm_model.compile(loss='mse', optimizer='adam')

    model = lstm_model.fit(X_train, y_train, epochs=50, batch_size=100,
                           validation_data=(X_test, y_test), shuffle=False)
    yh_pred = model.predict(X_pred).flatten()
    yh_test = model.predict(X_test).flatten()
    return yh_test, yh_pred


def train_lstm_model(model_func, param, signal_name='XGB400', search_times=0):
    param_copy = param.copy()
    select_num = param_copy.pop('select_num')
    lookback = param_copy.pop('lookback')

    long_dic = {}
    short_dic = {}
    long_pred = {}
    short_pred = {}
    long_true = {}
    short_true = {}

    for mh in model_month:
        test_end = calc_end_date(mh)
        test_start = get_pre_trade_date(test_end, 38)
        train_end = get_pre_trade_date(test_start, 2)
        train_start = calc_start_date(mh, 36)
        pred_start = get_pre_trade_date(test_end, -2)
        pred_end = min(get_pre_trade_date(calc_end_date(all_model_month[all_model_month.index(mh) + 1]), -1),
                       date_list[-1])

        if os.path.exists(f'{select_address}/MixFactor/{mh}_long.pkl'):
            long_list = pd.read_pickle(f'{select_address}/MixFactor/{mh}_long.pkl')
        else:
            os.makedirs(f'{select_address}/MixFactor/{mh}_long.pkl', exist_ok=True)
            long_list = pd.read_pickle(f'{select_address}/MixFactorLongAvailable.pkl').index
            long_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in long_list}).T
            long_list['mix_IC'] = long_list['IC'] + long_list['多头IC']
            long_list['mix_mdd'] = long_list['回撤期多头占比'] / long_list['多头占比'] * long_list['回撤期多头年化']
            long_list['score'] = long_list['mix_IC'].rank() + long_list['mix_mdd'].rank()
            long_list = long_list.sort_values('score', ascending=False).head(select_num)
            pd.to_pickle(long_list, f'{select_address}/MixFactor/{mh}_long.pkl')
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


def train_xgb_model(model_func, param, signal_name='XGB400', search_times=0, search_flag=True):
    hyper_search_signal_path = '/data/group/800442/800319/Timing/BackTest/Signal/hyper_search/'
    signal_path = '/data/group/800442/800319/Timing/BackTest/Signal/'
    param_copy = param.copy()
    select_num = param_copy.pop('select_num')

    param_copy.update({
        'silent': 1,
    })

    long_dic = {}
    short_dic = {}
    long_pred = {}
    short_pred = {}
    long_true = {}
    short_true = {}
    for mh in model_month:
        print(mh)
        test_end = calc_end_date(mh)
        test_start = get_pre_trade_date(test_end, 38)
        train_end = get_pre_trade_date(test_start, 2)
        train_start = calc_start_date(mh, 36)
        pred_start = get_pre_trade_date(test_end, -2)
        pred_end = min(get_pre_trade_date(calc_end_date(all_model_month[all_model_month.index(mh) + 1]), -1),
                       date_list[-1])

        if os.path.exists(f'{select_address}/MixFactor/{mh}_long.pkl'):
            long_list = pd.read_pickle(f'{select_address}/MixFactor/{mh}_long.pkl')
        else:
            os.makedirs(f'{select_address}/MixFactor/', exist_ok=True)
            long_list = pd.read_pickle(f'{select_address}/MixFactorLongAvailable.pkl').index
            long_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in long_list}).T
            long_list['mix_IC'] = long_list['IC'] + long_list['多头IC']
            long_list['mix_mdd'] = long_list['回撤期多头占比'] / long_list['多头占比'] * long_list['回撤期多头年化']
            long_list['score'] = long_list['mix_IC'].rank() + long_list['mix_mdd'].rank()
            long_list = long_list.sort_values('score', ascending=False).head(select_num)
            pd.to_pickle(long_list, f'{select_address}/MixFactor/{mh}_long.pkl')
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

        if X_pred.shape[0] != 0:
            yh1_test, yh1_pred = model_func(X_train, y_train, d_train, t_train, X_test, y_test,
                                            d_test, t_test, X_pred, d_pred, t_pred, param_copy)

            true_h1_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': y_pred}).set_index(['d', 't']).unstack()
            long_true[mh] = true_h1_pred

            h1_test = pd.DataFrame({'d': d_test, 't': t_test, 'yh': yh1_test}).set_index(['d', 't']).unstack()
            h1_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': yh1_pred}).set_index(['d', 't']).unstack()
            h1 = pd.concat([h1_test, h1_pred])
            h1 = pd.DataFrame(d2_move_max(h1.values, 40, 0.3), index=h1.index[39:], columns=h1.columns).reindex(
                h1_pred.index)
            long_dic[mh] = h1
            long_pred[mh] = h1_pred
        else:
            print(f'{mh}_long月份不符合准入条件！')

        if os.path.exists(f'{select_address}/MixFactor/{mh}_short.pkl'):
            short_list = pd.read_pickle(f'{select_address}/MixFactor/{mh}_short.pkl')
        else:
            os.makedirs(f'{select_address}/MixFactor/', exist_ok=True)
            short_list = pd.read_pickle(f'{select_address}/MixFactorShortAvailable.pkl').index
            short_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in short_list}).T
            short_list['mix_IC'] = short_list['IC'] + short_list['空头IC']
            short_list['mix_mdd'] = short_list['空头占比'] / short_list['回撤期空头占比'] * short_list['回撤期空头年化']
            short_list['score'] = short_list['mix_IC'].rank() + short_list['mix_mdd'].rank()
            short_list = short_list.sort_values('score', ascending=False).head(select_num)
            pd.to_pickle(short_list, f'{select_address}/MixFactor/{mh}_short.pkl')
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

        if X_pred.shape[0] != 0:
            yh2_test, yh2_pred = model_func(X_train, y_train, d_train, t_train, X_test, y_test,
                                            d_test, t_test, X_pred, d_pred, t_pred, param_copy)

            true_h2_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': y_pred}).set_index(['d', 't']).unstack()
            short_true[mh] = true_h2_pred

            h2_test = pd.DataFrame({'d': d_test, 't': t_test, 'yh': yh2_test}).set_index(['d', 't']).unstack()
            h2_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': yh2_pred}).set_index(['d', 't']).unstack()
            h2 = pd.concat([h2_test, h2_pred])
            h2 = pd.DataFrame(d2_move_min(h2.values, 40, 0.3), index=h2.index[39:], columns=h2.columns).reindex(
                h2_pred.index)
            short_dic[mh] = h2
            short_pred[mh] = h2_pred
        else:
            print(f'{mh}_short月份不符合准入条件！')

    total_long_pred = pd.concat([long_pred[m] for m in long_pred.keys()], axis=0)
    total_short_pred = pd.concat([short_pred[m] for m in short_pred.keys()], axis=0)
    total_long_true = pd.concat([long_true[m] for m in long_pred.keys()], axis=0)
    total_short_true = pd.concat([short_true[m] for m in short_pred.keys()], axis=0)

    # 为了方便直接读取进行回测
    long_df = pd.concat([long_dic[x] for x in model_month])
    short_df = pd.concat([short_dic[x] for x in model_month])
    long_pred = pd.concat([long_pred[x] for x in model_month])
    short_pred = pd.concat([short_pred[x] for x in model_month])
    signal = ((long_df > 0) & (short_df == 0)).astype('float64') - short_df.astype('float64')
    if search_flag:
        if not os.path.exists(f'{hyper_search_signal_path}{search_times}/'):
            os.makedirs(f'{hyper_search_signal_path}{search_times}/', exist_ok=True)
        signal.to_pickle(f'{hyper_search_signal_path}{search_times}/{signal_name}.pkl')
        long_pred.to_pickle(f'{hyper_search_signal_path}{search_times}/long_pred_{signal_name}.pkl')
        short_pred.to_pickle(f'{hyper_search_signal_path}{search_times}/short_pred_{signal_name}.pkl')
    else:
        if not os.path.exists(f'{signal_path}/'):
            os.makedirs(f'{signal_path}/', exist_ok=True)
        signal.to_pickle(f'{signal_path}/{signal_name}.pkl')
        long_pred.to_pickle(f'{signal_path}/long_pred_{signal_name}.pkl')
        short_pred.to_pickle(f'{signal_path}/short_pred_{signal_name}.pkl')

    return total_long_pred, total_short_pred, total_long_true, total_short_true


def train_xgb_model_dc(model_func, param, signal_name='XGB400_dc', search_times=0, search_flag=True):
    hyper_search_signal_path = f'/data/group/800442/800319/Timing/BackTest/Signal/hyper_search_{signal_name}/'
    signal_path = '/data/group/800442/800319/Timing/BackTest/Signal/'
    param_copy = param.copy()
    select_num = param_copy.pop('select_num')

    param_copy.update({
        'silent': 1,
    })

    long_dic = {}
    short_dic = {}
    long_pred = {}
    short_pred = {}
    long_true = {}
    short_true = {}
    for mh in model_month:
        print(mh)
        test_end = calc_end_date(mh)
        test_start = get_pre_trade_date(test_end, 38)
        train_end = get_pre_trade_date(test_start, 2)
        train_start = calc_start_date(mh, 36)
        pred_start = get_pre_trade_date(test_end, -2)
        pred_end = min(get_pre_trade_date(calc_end_date(all_model_month[all_model_month.index(mh) + 1]), -1),
                       date_list[-1])

        if os.path.exists(f'{select_address}/MixFactor{signal_name}/{mh}_long.pkl'):
            long_list = pd.read_pickle(f'{select_address}/MixFactor{signal_name}/{mh}_long.pkl')
        else:
            os.makedirs(f'{select_address}/MixFactor{signal_name}/', exist_ok=True)
            long_list1 = pd.read_pickle(f'{select_address}/MixFactorLongAvailable.pkl').index.tolist()
            long_list2 = pd.read_pickle(f'{fflong_address}/fflong_final_available.pkl').index.tolist()
            long_list2 = [str(x)[:-4] for x in long_list2]
            long_list = long_list1 + long_list2
            long_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in long_list}).T
            long_list['mix_IC'] = long_list['IC'] + long_list['多头IC']
            long_list['mix_mdd'] = long_list['回撤期多头占比'] / long_list['多头占比'] * long_list['回撤期多头年化']
            long_list['score'] = long_list['mix_IC'].rank() + long_list['mix_mdd'].rank()
            long_list = long_list.sort_values('score', ascending=False).head(select_num)
            pd.to_pickle(long_list, f'{select_address}/MixFactor{signal_name}/{mh}_long.pkl')
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

        if X_pred.shape[0] != 0:
            yh1_test, yh1_pred = model_func(X_train, y_train, d_train, t_train, X_test, y_test,
                                            d_test, t_test, X_pred, d_pred, t_pred, param_copy)

            true_h1_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': y_pred}).set_index(['d', 't']).unstack()
            long_true[mh] = true_h1_pred

            h1_test = pd.DataFrame({'d': d_test, 't': t_test, 'yh': yh1_test}).set_index(['d', 't']).unstack()
            h1_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': yh1_pred}).set_index(['d', 't']).unstack()
            h1 = pd.concat([h1_test, h1_pred])
            h1 = pd.DataFrame(d2_move_max(h1.values, 40, 0.3), index=h1.index[39:], columns=h1.columns).reindex(
                h1_pred.index)
            long_dic[mh] = h1
            long_pred[mh] = h1_pred
        else:
            print(f'{mh}_long月份不符合准入条件！')

        if os.path.exists(f'{select_address}/MixFactor{signal_name}/{mh}_short.pkl'):
            short_list = pd.read_pickle(f'{select_address}/MixFactor{signal_name}/{mh}_short.pkl')
        else:
            os.makedirs(f'{select_address}/MixFactor/', exist_ok=True)
            short_list1 = pd.read_pickle(f'{select_address}/MixFactorShortAvailable.pkl').index.tolist()
            short_list2 = pd.read_pickle(f'{fflong_address}/fflong_final_available.pkl').index.tolist()
            short_list2 = [str(x)[:-4] for x in short_list2]
            short_list = short_list1 + short_list2
            short_list = pd.DataFrame({x: load_timing_factor_test(x, mh) for x in short_list}).T
            short_list['mix_IC'] = short_list['IC'] + short_list['空头IC']
            short_list['mix_mdd'] = short_list['空头占比'] / short_list['回撤期空头占比'] * short_list['回撤期空头年化']
            short_list['score'] = short_list['mix_IC'].rank() + short_list['mix_mdd'].rank()
            short_list = short_list.sort_values('score', ascending=False).head(select_num)
            pd.to_pickle(short_list, f'{select_address}/MixFactor{signal_name}/{mh}_short.pkl')
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

        if X_pred.shape[0] != 0:
            yh2_test, yh2_pred = model_func(X_train, y_train, d_train, t_train, X_test, y_test,
                                            d_test, t_test, X_pred, d_pred, t_pred, param_copy)

            true_h2_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': y_pred}).set_index(['d', 't']).unstack()
            short_true[mh] = true_h2_pred

            h2_test = pd.DataFrame({'d': d_test, 't': t_test, 'yh': yh2_test}).set_index(['d', 't']).unstack()
            h2_pred = pd.DataFrame({'d': d_pred, 't': t_pred, 'yh': yh2_pred}).set_index(['d', 't']).unstack()
            h2 = pd.concat([h2_test, h2_pred])
            h2 = pd.DataFrame(d2_move_min(h2.values, 40, 0.3), index=h2.index[39:], columns=h2.columns).reindex(
                h2_pred.index)
            short_dic[mh] = h2
            short_pred[mh] = h2_pred
        else:
            print(f'{mh}_short月份不符合准入条件！')

    total_long_pred = pd.concat([long_pred[m] for m in long_pred.keys()], axis=0)
    total_short_pred = pd.concat([short_pred[m] for m in short_pred.keys()], axis=0)
    total_long_true = pd.concat([long_true[m] for m in long_pred.keys()], axis=0)
    total_short_true = pd.concat([short_true[m] for m in short_pred.keys()], axis=0)

    # 为了方便直接读取进行回测
    long_df = pd.concat([long_dic[x] for x in model_month])
    short_df = pd.concat([short_dic[x] for x in model_month])
    long_pred = pd.concat([long_pred[x] for x in model_month])
    short_pred = pd.concat([short_pred[x] for x in model_month])
    signal = ((long_df > 0) & (short_df == 0)).astype('float64') - short_df.astype('float64')
    if search_flag:
        if not os.path.exists(f'{hyper_search_signal_path}{search_times}/'):
            os.makedirs(f'{hyper_search_signal_path}{search_times}/', exist_ok=True)
        signal.to_pickle(f'{hyper_search_signal_path}{search_times}/{signal_name}.pkl')
        long_pred.to_pickle(f'{hyper_search_signal_path}{search_times}/long_pred_{signal_name}.pkl')
        short_pred.to_pickle(f'{hyper_search_signal_path}{search_times}/short_pred_{signal_name}.pkl')
    else:
        if not os.path.exists(f'{signal_path}/'):
            os.makedirs(f'{signal_path}/', exist_ok=True)
        signal.to_pickle(f'{signal_path}/{signal_name}.pkl')
        long_pred.to_pickle(f'{signal_path}/long_pred_{signal_name}.pkl')
        short_pred.to_pickle(f'{signal_path}/short_pred_{signal_name}.pkl')

    return total_long_pred, total_short_pred, total_long_true, total_short_true


if __name__ == '__main__':
    from HANXU.Timing.hyper_param_search.hyper_param_space import best_hyper_param_space
    train_xgb_model(timing_xgb_model, best_hyper_param_space, signal_name='XGB400', search_times=0,
                    search_flag=False)
