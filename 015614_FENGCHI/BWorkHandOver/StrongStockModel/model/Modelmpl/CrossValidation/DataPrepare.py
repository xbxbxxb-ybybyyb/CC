from dataApi.tradeDate import get_date_range, get_pre_trade_date
from dataApi.getData import get_daily_1factor
import numpy as np
import pandas as pd
import time
import os


def load_fix_data(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                  model_time_len=1, freq=7, address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/idx_date.npy' % address)
    idx_code = np.load('%s/idx_code.npy' % address)
    idx_time = np.load('%s/idx_time.npy' % address)

    time_len = idx_time.shape[0]

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_code = idx_code[choose, None].repeat(freq + model_time_len - 1, axis=1)
        idx_time = idx_time[None, 1 - freq - model_time_len:].repeat(choose.sum(), axis=0)

    fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r', offset=128)
    real_y_shape = fp.shape[0] // freq - starts
    del fp
    real_y_shape = 0 if real_y_shape < 0 else (real_y_shape if real_y_shape < shape else shape)
    real_y_choose = (
            np.arange(choose[:starts + real_y_shape].shape[0])[choose[:starts + real_y_shape]] - starts).tolist()
    real_y_choose = slice(None) if len(real_y_choose) == real_y_shape else real_y_choose

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    X = np.empty((len(factor_list), len(choose), freq + model_time_len - 1), dtype=np.float32)
    y = np.empty((len(choose), freq), dtype=np.float32)
    nolimit = np.empty((len(choose), freq), dtype=np.bool)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/{f}.npy', dtype='float32', mode='r',
                       shape=(shape, time_len), offset=starts * time_len * 4 + 128)
        X[j] = fp[choose, 1 - freq - model_time_len:]
        del fp

    if not real_y_shape:
        y[:] = np.nan
        nolimit[:] = False
    else:
        fp = np.memmap(f'{address}/future.npy', dtype='float32', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq * 4 + 128)
        y[:real_y_shape] = fp[real_y_choose, :]
        y[real_y_shape:] = np.nan

        fp = np.memmap(f'{address}/nolimit.npy', dtype='bool', mode='r',
                       shape=(real_y_shape, freq), offset=starts * freq + 128)
        nolimit[:real_y_shape] = fp[real_y_choose, :]
        nolimit[real_y_shape:] = False

    if return_idx:
        return X, y, nolimit, idx_date, idx_code, idx_time
    else:
        return X, y, nolimit


def load_fix_mv(start_date=20140801, end_date=20140901, factor_list=None, code_list=None, return_idx=True,
                address='/data/group/800319/HFfactor/RealTimeFixRollRobust/'):
    date_list = get_date_range(start_date, end_date) if end_date else sorted(start_date)

    idx_date = np.load('%s/data/idx_date.npy' % address)
    idx_code = np.load('%s/data/idx_code.npy' % address)

    starts = (idx_date < date_list[0]).sum()
    shape = (idx_date <= date_list[-1]).sum() - starts

    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date

    if code_list:
        code_list.sort()
        # TODO: idx_code not sorted
        choose1 = np.take(np.arange(len(code_list)), np.searchsorted(code_list, idx_code), mode='clip')
        choose1 = np.asanyarray(code_list)[choose1] == idx_code
        choose &= choose1

    if return_idx:
        idx_date = idx_date[choose]
        idx_code = idx_code[choose]

    choose = (np.arange(choose.shape[0])[choose] - starts).tolist()
    mean = np.empty((len(factor_list), len(choose)), dtype=np.float64)
    std = np.empty((len(factor_list), len(choose)), dtype=np.float64)
    choose = slice(None) if len(choose) == shape else choose

    for j, f in enumerate(factor_list):
        fp = np.memmap(f'{address}/mean/{f}.npy', dtype='float64', mode='r',
                       shape=shape, offset=starts * 8 + 128)
        mean[j] = fp[choose]
        del fp

        fp = np.memmap(f'{address}/std/{f}.npy', dtype='float64', mode='r',
                       shape=shape, offset=starts * 8 + 128)
        std[j] = fp[choose]
        del fp

    if return_idx:
        return mean, std, idx_date, idx_code
    else:
        return mean, std


def feature_engineering(X, y, nolimit, *args, limit=0.2, model_time_len=1, freq=7):
    if model_time_len > 1:
        X = np.lib.stride_tricks.as_strided(X, shape=(X.shape[0], X.shape[1], freq, X.shape[2] - freq + 1),
                                            strides=(X.strides[0], X.strides[1], X.strides[2], X.strides[2]))
        X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], X.shape[3]).transpose(1, 2, 0)

    else:
        X = X.reshape(X.shape[0], X.shape[1] * X.shape[2], model_time_len).transpose(1, 2, 0)

    y = y.flatten()
    nolimit = nolimit.flatten()
    valid = ((X == 0).sum(axis=2) < limit * X.shape[2]).all(axis=1) & np.isfinite(y) & nolimit

    valid_samples = valid.sum()
    print(time.strftime('%Y-%m-%d %H:%M:%S'), 'feature_engineering %s / %s = %s%%' % (
        valid_samples, y.shape[0], round(valid_samples / y.shape[0] * 100, 1)))

    X = X[valid]
    y = y[valid]

    dic = {}
    for arg in range(len(args)):
        dic[arg] = args[arg].flatten()[valid]

    if model_time_len == 1:
        X = X[:, 0]

    return (X, y) + tuple(dic.values())


def split_train_predict(train_days=200, predict_days=10, future_day=1, pred_start=20161221, pred_end=20210616,
                        load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'):
    idx_date = np.load('%s/idx_date.npy' % load_address)
    pred_end = pred_end if pred_end else idx_date[-1]
    pred_end = min(pred_end, get_pre_trade_date(offset=1, dividing_point=21))
    date_list = get_date_range(idx_date[0], pred_end)
    predict_ends = sorted(date_list[-1: train_days + predict_days + future_day - 2: -predict_days])
    predict_starts = [date_list[date_list.index(x) - predict_days + 1] for x in predict_ends]
    predict_starts = [x for x in predict_starts if x >= pred_start] if pred_start else predict_starts
    predict_ends = predict_ends[-len(predict_starts):]
    train_ends = [date_list[date_list.index(x) - future_day - 1] for x in predict_starts]
    train_starts = [date_list[date_list.index(x) - train_days + 1] for x in train_ends]
    model_index = list(range(len(predict_ends)))
    model_date_list = {k: (train_starts[k], train_ends[k], predict_starts[k], predict_ends[k]) for k in model_index}
    return model_date_list


def split_train_test(start_date, end_date, test_date_idx):
    date_list = get_date_range(start_date, end_date)
    test_dates = sorted([date_list[x] for x in test_date_idx])
    train_dates = sorted(list(set(date_list) - set(test_dates)))
    return train_dates, test_dates


def infer_code_list(start_date, end_date, load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'):
    idx_date = np.load('%s/idx_date.npy' % load_address)
    idx_code = np.load('%s/idx_code.npy' % load_address)
    date_list = get_date_range(start_date, end_date)
    choose = np.take(np.arange(len(date_list)), np.searchsorted(date_list, idx_date), mode='clip')
    choose = np.asanyarray(date_list)[choose] == idx_date
    code_list = sorted(list(set(idx_code[choose])))
    return code_list


def rank_code_list(start_date, end_date, code_list=None, item='mkt_cap_ard',
                   load_address='/data/group/800319/HFfactor/RealTimeFixRollRobust/data/'):
    code_list = code_list if code_list else infer_code_list(start_date, end_date, load_address)
    date_list = get_date_range(start_date, end_date)
    ranked_list = get_daily_1factor(item, date_list, code_list).mean().sort_values(ascending=False).index.to_list()
    return ranked_list


def select_factor_list(train_end, month_freq=6, file='/data/user/015836/HFmodel/NNResearch/factor_score.pkl'):
    df = pd.read_pickle(file).iloc[:, ::month_freq]
    change_days = df.columns.to_list()
    change_day = ([change_days[0]] + [x for x in change_days if x < train_end])[-1]
    select = df[change_day].sort_values(ascending=False)
    return select


def prepare_model_fold(model_name, model_root):
    sub_folds = ['conf', 'train', 'test', 'pred', 'analyse']
    for f in sub_folds:
        path = f'{model_root}/{model_name}/{f}/'
        if not os.path.exists(path):
            os.makedirs(path)
