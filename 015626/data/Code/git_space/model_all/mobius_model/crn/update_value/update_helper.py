import os
import pickle
import numpy as np
import pandas as pd
import bottleneck as bk
from bisect import bisect_left
from multiprocessing import Pool
from toolkit.multifactor.utility.dt import get_trading_day_offset

import onnx
import onnxruntime as ort

index_root_dict = {
    'IH': '/data/user/020529/share/mobius_prod/model_update/rank_index/ih_60000_25_75',
    'IF': '/data/user/020529/share/mobius_prod/model_update/rank_index/if_60000_25_75',
    'IC': '/data/user/020529/share/mobius_prod/model_update/rank_index/ic_60000_25_75',
    'IM': '/data/user/020529/share/mobius_prod/model_update/rank_index/im_60000_25_75',
}


def update_model(strategy, model_times, num_models, factor_root, model_root, value_root, update_date_list, rank1=4800, rank2=2400):
    # load factors
    YMD = '%Y%m%d'
    str_date = get_trading_day_offset(update_date_list[0], -1)[0].strftime(YMD)
    end_date = update_date_list[-1]
    factor_path = os.path.join(model_root, strategy, 'factor_name_mapping.csv')
    factor_list = pd.read_csv(factor_path)
    factor_list = factor_list['factor_name'].to_list()
    factor_all = fetch_factor(factor_root, factor_list, str_date, end_date)
    factor_all = fill_inf_and_nan(factor_all)

    # update model_value
    num_processes = 0
    for name, time_list in model_times.items():
        num_processes += len(time_list)
    for update_date in update_date_list:
        # prepare inputs
        str_date = (pd.Timestamp(update_date) - pd.Timedelta(days=30)).strftime(YMD)
        end_date = update_date
        inputs = factor_all[str_date:end_date]

        # calculate signal (update model_raw_itr)
        pool = Pool(processes=num_processes)
        for name, time_list in model_times.items():
            for time in time_list:
                pool.apply_async(calculate_signal, args=(value_root, model_root, strategy, name, time, update_date, num_models, inputs), error_callback=print_error)
        pool.close()
        pool.join()

        # update model_raw
        for name, time_list in model_times.items():
            update_model_raw(value_root, strategy, name, time_list, update_date)

        # update model_norm
        work_space = os.path.join(value_root, strategy)
        update_model_norm(work_space, update_date, rank1, rank2)

        # update model_norm2
        index_root = index_root_dict[strategy.split('_')[1].upper()]
        update_model_norm2(work_space, update_date, index_root)
    return None


def fetch_factor(factor_root, factor_list, str_date, end_date):
    factor_all = []
    for factor_name in factor_list:
        factor_path = os.path.join(factor_root, f'{factor_name}.h5')
        factor = pd.read_hdf(factor_path)
        assert isinstance(factor, pd.DataFrame)
        factor = factor.loc[str_date:end_date]
        factor = factor.between_time(start_time='09:30', end_time='14:56')
        factor_all.append(factor)
    factor_all = pd.concat(factor_all, axis=1, join='outer')
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique
    assert np.all(np.array(factor_all.groupby(factor_all.index.date).size() == 237))
    return factor_all


def fill_inf_and_nan(x):
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.fillna(0.0)
    return x


def calculate_signal(value_root, model_root, strategy, model_name, return_time, update_date, num_models, inputs):
    signal_all = {}
    for model_idx in range(num_models):
        # load model
        model_path = os.path.join(model_root, strategy, model_name, f'{model_name}_{return_time}_{model_idx}.onnx')
        model_onnx = onnx.load(model_path)
        onnx.checker.check_model(model_onnx)
        model_onnx = model_onnx.SerializeToString()
        ort_sess = ort.InferenceSession(model_onnx)

        # load input list
        input_path = os.path.join(model_root, strategy, model_name, f'{model_name}_{return_time}_{model_idx}.csv')
        input_list = pd.read_csv(input_path)
        input_list = input_list['factor_name'].to_list()

        # prepare model input
        x_pd = inputs[input_list]
        input_shape = ort_sess.get_inputs()[0].shape
        if len(input_shape) == 2:
            pred_index = x_pd.index
            pred_input = x_pd.values
        elif len(input_shape) == 3:
            time_step = input_shape[1]
            pred_index = x_pd.iloc[time_step - 1:].index
            pred_input = transform_2d_to_3d(x_pd.values, time_step)
        else:
            print('the dimension of x is not 2 or 3')
            raise Exception

        # calculate signal
        y_np = []
        for t in range(pred_input.shape[0]):
            x_np = pred_input[t:t + 1]
            res = ort_sess.run(None, {ort_sess.get_inputs()[0].name: x_np.astype(np.float32)})
            y_np.append(res[0])
        y_np = np.concatenate(y_np, axis=0)
        y_pd = pd.Series(y_np, index=pred_index)
        signal_all[model_idx] = y_pd[update_date:update_date]
    signal_all = pd.DataFrame(signal_all)

    output_path = os.path.join(value_root, strategy, 'model_value', 'model_raw_itr', update_date, f'{model_name}_{return_time}.pkl')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(output_path)
    save_pickle(signal_all, output_path)
    return None


def update_model_raw(value_root, strategy, model_name, return_time_list, update_date):
    signal_new = {}
    for return_time in return_time_list:
        signal_path = os.path.join(value_root, strategy, 'model_value', 'model_raw_itr', update_date, f'{model_name}_{return_time}.pkl')
        signal_all = load_pickle(signal_path)
        signal_avg = signal_all.mean(axis=1)
        signal_new[f'{model_name}_{return_time}'] = signal_avg
    signal_new = pd.DataFrame(signal_new)

    latest_date = None
    date_root = os.path.join(value_root, strategy, 'model_value', 'model_raw')
    date_list = os.listdir(date_root)
    date_list = sorted(date_list, reverse=False)
    for date in date_list:
        if int(date) < int(update_date):
            latest_date = str(date)
    assert latest_date is not None, 'miss historical raw value'
    signal_path = os.path.join(value_root, strategy, 'model_value', 'model_raw', latest_date, f'{model_name}.pkl')
    signal_old = load_pickle(signal_path)
    signal_raw = pd.concat([signal_old, signal_new], axis=0)

    output_path = os.path.join(value_root, strategy, 'model_value', 'model_raw', update_date, f'{model_name}.pkl')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    print(output_path)
    save_pickle(signal_raw, output_path)
    return None


def update_model_norm(work_space, update_date, rank1, rank2):
    model_name_list = []
    for file_name in os.listdir(os.path.join(work_space, 'model_value', 'model_raw', update_date)):
        name, ext = os.path.splitext(file_name)
        model_name_list.append(name)
    model_name_list.sort()

    pred_comb2 = []
    for model_name in model_name_list:
        signal_path = os.path.join(work_space, 'model_value', 'model_raw', update_date, f'{model_name}.pkl')
        signal_raw = load_pickle(signal_path)

        signal_all = ts_rank(signal_raw, rank1)
        signal_avg = signal_all.mean(axis=1)
        signal_norm = signal_avg.to_frame(name=model_name)

        output_path = os.path.join(work_space, 'model_value', 'model_norm', update_date, f'{model_name}.pkl')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(output_path)
        save_pickle(signal_norm, output_path)

        pred_comb2.append(signal_norm)
    pred_comb2 = pd.concat(pred_comb2, axis=1)
    pred_comb2 = pred_comb2.mean(axis=1)
    pred_comb2 = ts_rank(pred_comb2, rank2)

    output_path = os.path.join(work_space, 'model_value', 'model_norm', update_date, 'pred_comb2.pkl')
    print(output_path)
    save_pickle(pred_comb2, output_path)
    return None


def update_model_norm2(work_space, update_date, index_root):
    model_name_list = []
    for file_name in os.listdir(os.path.join(work_space, 'model_value', 'model_raw', update_date)):
        name, ext = os.path.splitext(file_name)
        model_name_list.append(name)
    model_name_list.sort()

    pred_comb2 = []
    for model_name in model_name_list:
        signal_path = os.path.join(work_space, 'model_value', 'model_raw', update_date, f'{model_name}.pkl')
        signal_raw = load_pickle(signal_path)

        signal_date = update_date
        signal_temp = signal_raw[signal_date]
        signal_norm = pd.DataFrame(np.full(signal_temp.shape, np.nan), index=signal_temp.index, columns=signal_temp.columns)
        index_path = os.path.join(index_root, f'{signal_date}.pkl')
        index_list = load_pickle(index_path)
        index_diff = pd.to_datetime(index_list).difference(signal_raw.index)
        if len(index_diff) > 0:
            fmt = '%Y-%m-%d'
            print(f'[{signal_date}] miss historical value: {len(index_diff)} points, from {index_diff[0].strftime(fmt)} to {index_diff[-1].strftime(fmt)}')
        else:
            signal_base = signal_raw[signal_raw.index.isin(index_list)]
            for col in signal_raw.columns:
                a = np.sort(signal_base[col].values)
                signal_norm[col] = [bisect_left(a, x) for x in signal_temp[col].values]
            signal_norm = signal_norm.div(len(signal_base)).mul(2).sub(1)
        signal_new = signal_norm.mean(axis=1).to_frame(name=model_name)

        latest_date = None
        date_root = os.path.join(work_space, 'model_value', 'model_norm2')
        date_list = os.listdir(date_root)
        date_list = sorted(date_list, reverse=False)
        for date in date_list:
            if int(date) < int(update_date):
                latest_date = str(date)
        assert latest_date is not None, 'miss historical raw value'
        signal_path = os.path.join(work_space, 'model_value', 'model_norm2', latest_date, f'{model_name}.pkl')
        signal_old = load_pickle(signal_path)
        signal_norm2 = pd.concat([signal_old, signal_new], axis=0)

        output_path = os.path.join(work_space, 'model_value', 'model_norm2', update_date, f'{model_name}.pkl')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        print(output_path)
        save_pickle(signal_norm2, output_path)

        pred_comb2.append(signal_norm2)
    pred_comb2 = pd.concat(pred_comb2, axis=1)
    pred_comb2 = pred_comb2.mean(axis=1)

    output_path = os.path.join(work_space, 'model_value', 'model_norm2', update_date, 'pred_comb2.pkl')
    print(output_path)
    save_pickle(pred_comb2, output_path)
    return None


def transform_2d_to_3d(x_2d, time_step):
    x_len = x_2d.shape[0]
    if x_len < time_step:
        print('the length of x is shorter than time_step')
        raise Exception
    x_3d = []
    for t in range(x_len - time_step + 1):
        xt = x_2d[t:t + time_step, :]
        x_3d.append(xt)
    x_3d = np.array(x_3d)
    return x_3d


def ts_rank(data, d):
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0), index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0), index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
        else:
            output = None
    return output


def save_pickle(data, path):
    with open(path, mode='wb') as file:
        pickle.dump(data, file, protocol=3)
    return None


def load_pickle(path):
    with open(path, mode='rb') as file:
        data = pickle.load(file)
    return data


def print_error(error):
    print('Error: {}'.format(error))
    return None
