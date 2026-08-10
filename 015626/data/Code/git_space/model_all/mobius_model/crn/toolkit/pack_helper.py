import os
import csv
import json
import shutil
import numpy as np
import pandas as pd
import bottleneck as bk
from bisect import bisect_left
from config.base import root, pack_model_root, pack_value_root, index_root_dict
from framework.utils import load_pickle, save_pickle


def set_model_file(model_config, factor_base, ticker_type, update_date, return_time_list, random_seed_list):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    model_name = model_config['export_name']

    file_root = os.path.join(root, 'model', 'model_file', identifier, update_date)
    os.makedirs(file_root, exist_ok=True)
    print(f'set model_file: {file_root}', flush=True)

    for return_time in return_time_list:
        model_idx = 0
        for random_seed in random_seed_list:
            home = os.path.join(root, 'model', 'model_prod', identifier, update_date, f'time_{return_time}', f'seed_{random_seed}')
            record_path = os.path.join(home, 'model_record.pkl')
            record = load_pickle(record_path)
            factor_list = record['factor_list']
            for k in range(5):
                src_path = os.path.join(home, f'model.{k}.onnx')
                dst_path = os.path.join(file_root, f'{model_name}_{return_time}_{model_idx}.onnx')
                shutil.copyfile(src_path, dst_path)
                output_path = os.path.join(file_root, f'{model_name}_{return_time}_{model_idx}_factor_list.pkl')
                save_pickle(factor_list, output_path)
                model_idx += 1
    return None


def set_model_pred(model_config, factor_base, ticker_type, update_date, verify_date_list, return_time_list, random_seed_list):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    model_name = model_config['export_name']

    pred_root = os.path.join(root, 'model', 'model_pred', identifier, update_date)
    os.makedirs(pred_root, exist_ok=True)
    print(f'set model_pred: {pred_root}', flush=True)

    for return_time in return_time_list:
        signal_list = []
        for i, verify_date in enumerate(verify_date_list):
            prediction_all = {}
            model_idx = 0
            for random_seed in random_seed_list:
                home = os.path.join(root, 'model', 'model_temp', identifier, verify_date, f'time_{return_time}', f'seed_{random_seed}')
                for k in range(5):
                    prediction_path = os.path.join(home, f'prediction.{k}.pkl')
                    prediction = load_pickle(prediction_path)
                    prediction_all[model_idx] = prediction
                    model_idx += 1
            prediction_all = pd.DataFrame(prediction_all)
            if i + 1 < len(verify_date_list):
                str_date = (pd.Timestamp(verify_date) + pd.Timedelta(days=1)).strftime('%Y%m%d')
                end_date = verify_date_list[i + 1]
            else:
                str_date = (pd.Timestamp(verify_date) + pd.Timedelta(days=1)).strftime('%Y%m%d')
                end_date = update_date
            prediction_cut = prediction_all[str_date:end_date]
            signal_list.append(prediction_cut)
        signal_all = pd.concat(signal_list, axis=0)
        output_path = os.path.join(pred_root, f'{model_name}_{return_time}.pkl')
        save_pickle(signal_all, output_path)
    return None


def set_model_trade(strategy, model_config, factor_base, ticker_type, update_date):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    model_name = model_config['export_name']

    work_space = os.path.join(pack_model_root, f'{update_date}_{ticker_type[0:2].lower()}_{strategy}')
    print(f'set model_trade: {work_space}', flush=True)

    # copy model_file and factor_list
    src_root = os.path.join(root, 'model', 'model_file', identifier, update_date)
    dst_root = os.path.join(work_space, model_name)
    os.makedirs(dst_root, exist_ok=True)
    for file_name in os.listdir(src_root):
        name, ext = os.path.splitext(file_name)
        if ext != '.onnx':
            continue
        src_path = os.path.join(src_root, f'{name}.onnx')
        dst_path = os.path.join(dst_root, f'{name}.onnx')
        shutil.copyfile(src_path, dst_path)

        src_path = os.path.join(src_root, f'{name}_factor_list.pkl')
        dst_path = os.path.join(dst_root, f'{name}.csv')
        factor_list = load_pickle(src_path)
        with open(dst_path, mode='w', encoding='utf-8') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(['factor_name', 'model_input_name'])
            for idx, fac in enumerate(factor_list):
                csv_writer.writerow([fac, f'x{idx}'])
    return None


def set_model_update(strategy, model_config, factor_base, ticker_type, update_date, return_time_list, rank_period=4800, verbose=False):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    model_name = model_config['export_name']

    work_space = os.path.join(pack_value_root, f'{update_date}_{ticker_type[0:2].lower()}_{strategy}')
    print(f'set model_update: {work_space}', flush=True)

    # copy historical_value
    src_root = os.path.join(root, 'model', 'model_pred', identifier, update_date)
    dst_root = os.path.join(work_space, 'historical_value')
    os.makedirs(dst_root, exist_ok=True)
    for return_time in return_time_list:
        src_path = os.path.join(src_root, f'{model_name}_{return_time}.pkl')
        dst_path = os.path.join(dst_root, f'{model_name}_{return_time}.pkl')
        shutil.copyfile(src_path, dst_path)

    # initialize model_raw
    signal_dict = {}
    for return_time in return_time_list:
        signal_path = os.path.join(work_space, 'historical_value', f'{model_name}_{return_time}.pkl')
        signal_all = pd.read_pickle(signal_path)
        signal_avg = signal_all.mean(axis=1)
        signal_dict[f'{model_name}_{return_time}'] = signal_avg
    signal_raw = pd.DataFrame(signal_dict)
    output_path = os.path.join(work_space, 'model_value', 'model_raw', update_date, f'{model_name}.pkl')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_pickle(signal_raw, output_path)

    # initialize model_norm
    signal_all = ts_rank(signal_raw, rank_period)
    signal_avg = signal_all.mean(axis=1)
    signal_norm = signal_avg.to_frame(name=model_name)
    output_path = os.path.join(work_space, 'model_value', 'model_norm', update_date, f'{model_name}.pkl')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_pickle(signal_norm, output_path)

    # initialize model_norm2
    index_root = index_root_dict[ticker_type[0:2]]
    signal_list = []
    signal_date_list = pd.to_datetime(signal_raw.index.date).drop_duplicates().strftime('%Y%m%d').to_list()
    for signal_date in signal_date_list:
        signal_temp = signal_raw[signal_date]
        signal_norm = pd.DataFrame(np.full(signal_temp.shape, np.nan), index=signal_temp.index, columns=signal_temp.columns)
        index_path = os.path.join(index_root, f'{signal_date}.pkl')
        index_list = load_pickle(index_path)
        index_diff = pd.to_datetime(index_list).difference(signal_raw.index)
        if len(index_diff) > 0:
            if verbose:
                fmt = '%Y-%m-%d'
                print(f'[{signal_date}] miss historical value: {len(index_diff)} points, from {index_diff[0].strftime(fmt)} to {index_diff[-1].strftime(fmt)}', flush=True)
        else:
            signal_base = signal_raw[signal_raw.index.isin(index_list)]
            for col in signal_raw.columns:
                a = np.sort(signal_base[col].values)
                signal_norm[col] = [bisect_left(a, x) for x in signal_temp[col].values]
            signal_norm = signal_norm.div(len(signal_base)).mul(2).sub(1)
        signal_list.append(signal_norm)
    signal_all = pd.concat(signal_list, axis=0)
    signal_avg = signal_all.mean(axis=1)
    signal_norm = signal_avg.to_frame(name=model_name)
    output_path = os.path.join(work_space, 'model_value', 'model_norm2', update_date, f'{model_name}.pkl')
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    save_pickle(signal_norm, output_path)
    return None


def add_config_files(strategy, ticker_type, update_date):
    work_space = os.path.join(pack_model_root, f'{update_date}_{ticker_type[0:2].lower()}_{strategy}')

    name_list = []
    for model_name in os.listdir(work_space):
        if os.path.isfile(os.path.join(work_space, model_name)):
            continue
        for file_name in os.listdir(os.path.join(work_space, model_name)):
            name, ext = os.path.splitext(file_name)
            if ext == '.onnx':
                name_list.append(name)
    name_list.sort(key=lambda x: ('_'.join(x.split('_')[:-2]), int(x.split('_')[-2]), int(x.split('_')[-1])))

    item_list = []
    for name in name_list:
        item = {
            'parentPath': '_'.join(name.split('_')[:-2]),
            'groupName': '_'.join(name.split('_')[:-1]),
            'modelName': name,
            'modelFile': f'{name}.onnx',
            'factorListFile': f'{name}.csv',
        }
        item_list.append(item)

    config_path = os.path.join(work_space, 'model_config.json')
    with open(config_path, mode='w', encoding='utf-8') as file:
        json.dump(item_list, file, indent=4)

    a = item_list[0]['parentPath']
    b = item_list[0]['factorListFile']
    src_path = os.path.join(work_space, a, b)
    dst_path = os.path.join(work_space, 'factor_name_mapping.csv')
    shutil.copyfile(src_path, dst_path)
    return None


def copy_trade_to_update(strategy, ticker_type, update_date):
    src_path = os.path.join(pack_model_root, f'{update_date}_{ticker_type[0:2].lower()}_{strategy}')
    dst_path = os.path.join(pack_value_root, f'{update_date}_{ticker_type[0:2].lower()}_{strategy}', 'model_trade', f'{update_date}_{ticker_type[0:2].lower()}_{strategy}')
    if os.path.exists(dst_path):
        shutil.rmtree(dst_path)
    shutil.copytree(src_path, dst_path)
    return None


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
