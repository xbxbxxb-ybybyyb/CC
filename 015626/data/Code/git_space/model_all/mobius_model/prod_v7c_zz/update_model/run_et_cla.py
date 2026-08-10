import sys

sys.path.insert(0, '/data/user/020529/mobius_product_zz/code')

import gc
import numpy as np
import datetime as dt
from functools import partial

from multifactor.IO import IO
from strategy.fitting_model import pred_fit_extratree_cla_kf, get_train_test_sample, set_seed
from strategy.strategy_utility import predict_rolling_cs_wrapper2
from ts.utility.ts_utility import read_pickle, save_pickle, slice_by_minute, get_price_with_mask, get_calendar_info, get_dummies_helper
from ts.utility.ts_utility import calc_hpr_recent, calc_hpr, calc_ts_truncation, ts_align_fitting_data
from factor_utility.minute_tool import get_rebal_list_smart, get_minute_seg_dt, data_save_path
from minute_config_mobius import *

shuffle = False
model = 'et_cla'
pred_type = 'reg'

# if check_flag:
#     flag_wait(ftypes, fac_lib_date, flag_path_mobius,gap=flag_gap,expiration=flag_expiration)
for si in suffix_list:
    if isinstance(fac_path_dict[si], dict):
        if model not in fac_path_dict[si]:
            print('no need for %s in %s' % (model, si), flush=True)
            suffix_list.remove(si)
for suffix in suffix_list:
    fac_path = fac_path_dict[suffix] if isinstance(fac_path_dict[suffix], str) else fac_path_dict[suffix][model]
    pred_res_base = pred_res_base_dict[suffix]
    trade_contract = trade_contract_dict[suffix]
    hpr_spec_dict = hpr_spec_dd[suffix]
    print('config_info: %s ~ %s ~ %s | %s ~ %s' % (suffix, trade_contract, fac_lib_date, hpr_spec_dict[model], version_type), flush=True)

    fac_val = read_pickle(fac_path)
    fac_val = slice_by_minute(fac_val, slice_range).loc[:edate]
    sdate_val, edate_val = fac_val.index[0], fac_val.index[-1]
    print('%s ~ %s: %s' % (sdate_val, edate_val, str(fac_val.shape)), flush=True)
    print(fac_val.loc[fac_lib_date].iloc[-5:, :5].dropna(), flush=True)

    ### model setting
    res_base_path = os.path.join(pred_res_base, 'res_%s/%s/model_%s/%s' % (fac_lib_date, trade_contract[:2], filter_date, model))
    print(trade_contract, flush=True)
    print(res_base_path, flush=True)

    ####################################################################################################

    track_feature_importance = True
    return_score = False
    verbose = True
    plot_model = False

    params = {'n_estimators': 3000,
              'min_samples_split': 0.005,
              'max_features': 'auto',
              'criterion': 'gini',
              'bootstrap': False,
              'oob_score': False,
              'n_jobs': 24,
              'class_weight': 'balanced',
              'random_state': 2018}
    fit_pred_func = partial(pred_fit_extratree_cla_kf, fold_num=fold_num, params=params, verbose=verbose,
                            return_score=return_score, weight_type='abs_ret', stratified=True,
                            track_feature_importance=track_feature_importance,
                            return_misc=return_misc, return_model=return_model,
                            shuffle=shuffle)

    ####################################################################################################

    print('read price data', flush=True)
    print('#' * 40, flush=True)
    print('%s: %s - %s - %s' % (trade_contract, sdate, edate, train_s), flush=True)
    if price_type == 'future':
        minute_price_path = minute_future_path
        pred_price_use = pred_price
    elif price_type == 'spot':
        minute_price_path = minute_spot_path
        if pred_price == 'vwap':
            print('vwap not supported for spot', flush=True)
            raise Exception
        pred_price_use = pred_price + '_spot'
    elif price_type == 'fake':
        minute_price_path = minute_fake_path
        pred_price_use = pred_price + '_fake'
    elif price_type == 'future_fix':
        print('prep recent price dict for future_fix', flush=True)
        minute_price_path = minute_future_path
        fts_data_is = read_pickle(fts_path_is)
        fts_data_os = read_pickle(fts_path_os)
        recent_price_dict = get_price_with_mask(fts_data_is, fts_data_os)
        pred_price_use = pred_price
    else:
        raise RuntimeError('invalid price_type')

    print('price_type :%s | pred_price_use: %s' % (price_type, pred_price_use), flush=True)
    print('%s: %s' % (trade_contract, minute_price_path), flush=True)
    if price_type == 'fake':
        ts_price_minute = pd.read_hdf(minute_fake_path)
    else:
        dat_minute = IO.read_data([sdate, edate], alt=minute_price_path)
        index_minute_dict = {i: dat_minute.xs(i, level=1) for i in index_list}
        dat_index_minute = index_minute_dict[trade_contract]
        ts_price_minute = dat_index_minute[pred_price_use]
    ts_price_minute = slice_by_minute(ts_price_minute, slice_range)
    ts_price_minute = ts_price_minute.copy().loc[train_s:edate]
    print(ts_price_minute.tail(), flush=True)
    print('load price data done', flush=True)

    print('#' * 80, flush=True)
    print('prediction start ~ %s' % (trade_contract), flush=True)
    print('prep fitting data', flush=True)
    if version_type == 'one_shot':
        rebal_freq = rebal_freq_spec
    else:
        rebal_freq = get_rebal_list_smart(sdate_fit, edate, rebal_mode_dict)
    print(rebal_freq[-5:], flush=True)

    if use_dummy:
        print('create meta factor', flush=True)
        minute_duration = 60
        minute_block = get_minute_seg_dt(ts_price_minute, minute_duration)
        calendar_info = get_calendar_info(ts_price_minute)
        time_info = pd.concat([minute_block, calendar_info], axis=1)
        if add_mcount:
            minute_cnt = pd.DataFrame(ts_price_minute.groupby(ts_price_minute.index.date).cumcount(), columns=['minute_cnt'])
            time_info = pd.concat([time_info, minute_cnt], axis=1)
        time_dummies = get_dummies_helper(time_info)
        minute_seg_list = [i for i in time_dummies.columns if i.find('year') < 0]
        time_dummies = time_dummies[minute_seg_list]
        x = pd.concat([fac_val, time_dummies], axis=1)
    else:
        x = fac_val

    x = x.loc[train_s:]
    x[~np.isfinite(x)] = 0
    print(x.shape, flush=True)
    print(x.index[0], x.index[-1], flush=True)
    iter_list = hpr_spec_dict[model]
    res_save_path_dict = {iter_name: os.path.join(data_save_path, res_base_path, '%s_%d_r%d.pkl' % (model, iter_name, roll_day)) for iter_name in iter_list}
    res_dict_model = {}
    for iter_name in iter_list:
        print(iter_name, flush=True)
        print('training start - %s' % (model), flush=True)
        holding_period = iter_name
        if price_type == 'future_fix':
            y = calc_hpr_recent(recent_price_dict, holding_period, pred_price, trade_contract)
        else:
            y = calc_hpr(ts_price_minute, holding_period=holding_period, ret_shift=ret_shift)
        if hpr_trend:
            y = calc_hpr(ts_price_minute, holding_period=holding_period, ret_shift=ret_shift)
            past_num = max(1, int(holding_period / 2))
            print('calc hpr trend: %s minute | %s weight' % (past_num, past_weight), flush=True)
            past_ret = ts_price_minute / ts_price_minute.shift(past_num) - 1
            if trend_up:
                past_ret[past_ret < 0] = 0
            y = y + past_ret * past_weight
        y_slice = slice_by_minute(y, slice_range)
        x_slice = slice_by_minute(x, slice_range)
        if burn_overnight:
            minute_e = str(int(60 - holding_period - 4))
            eminute_str = '14%s' % (minute_e)
            slice_range_burn = [[930, 1129], [1300, int(eminute_str)]]
            print('burn_overnight ~ slice by %s' % (str(slice_range_burn)), flush=True)
            y_slice = slice_by_minute(y, slice_range_burn)
            x_slice = slice_by_minute(x, slice_range_burn)
            rebal_freq = [pd.Timestamp(dt.datetime.strftime(i, '%Y%m%d') + '-14:%s:00' % (minute_e)) for i in rebal_freq]

        if ts_trunc:
            y_slice = calc_ts_truncation(y_slice, roll_win=trunc_win, cut_limit=cut_limit, min_pct=min_pct_trunc)
        if pred_type == 'reg':
            y_use, x_use = ts_align_fitting_data(y_slice, x_slice, sdate=sdate, edate=edate, label_cut=None, fillna=True)
            y_train, y_test, x_train, x_test = get_train_test_sample(y_use, x_use)
        elif pred_type == 'cla':
            y_use, x_use, x_test = ts_align_fitting_data(y_slice, x_slice, sdate=sdate, edate=edate, label_cut=0, fillna=True)
            y_train, y_test, x_train, x_test = get_train_test_sample(y_use, x_use)

        set_seed()
        res_dict_model[iter_name] = predict_rolling_cs_wrapper2(y_use, x_use, roll_win, holding_period,
                                                                rebal_freq=rebal_freq, fit_pred_func=fit_pred_func, x_test=None,
                                                                test_run=test_run, expanding_window=expanding_window,
                                                                return_model=return_model,
                                                                process_dat_func=process_dat_func, process_list=process_list)
        save_pickle(res_dict_model[iter_name], res_save_path_dict[iter_name])
        del y_use, x_use, y_slice, x_slice
        for i in range(3): gc.collect()
    del fac_val, x, y, fit_pred_func
