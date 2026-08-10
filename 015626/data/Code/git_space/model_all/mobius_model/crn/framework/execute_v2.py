import os
import torch
import datetime
import numpy as np
import pandas as pd
from sklearn.model_selection import KFold
from config.base import fmt, root
from framework.logger import Logger
from framework.model_v2 import Model
from framework.utils import erase_daily_gaps, create_data_mask, normalize_return, fill_inf_and_nan, convert_to_prob, set_random_seed, save_pickle, load_pickle


def train(model_config, factor_base, ticker_type, update_date, return_time, random_seed, prod_version=True, save_info=True, show_info=True):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    start_time = datetime.datetime.now().strftime(fmt)
    print('[{}] train: {}, {}, {}, {}'.format(start_time, identifier, update_date, return_time, random_seed), flush=True)

    # make directory
    if prod_version:
        home = os.path.join(root, 'model', 'model_prod', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
    else:
        home = os.path.join(root, 'model', 'model_temp', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
    os.makedirs(home, exist_ok=True)

    # prepare data
    fac_path = os.path.join(root, 'data', 'factor', '{}.h5'.format(factor_base))
    ret_path = os.path.join(root, 'data', 'return', '{}.h5'.format(ticker_type))
    fac_all = pd.read_hdf(fac_path)
    ret_all = pd.read_hdf(ret_path)
    assert isinstance(fac_all, pd.DataFrame)
    assert isinstance(ret_all, pd.DataFrame)
    ret_all = ret_all[return_time]

    ins_str_date = fac_all.index[0].strftime('%Y%m%d')
    ins_end_date = update_date
    assert pd.Timestamp(ins_str_date) < pd.Timestamp(ins_end_date)
    fac_ins = fac_all.loc[ins_str_date:ins_end_date]
    ret_ins = ret_all.loc[ins_str_date:ins_end_date]

    num_minutes = model_config['num_minutes']
    assert np.all(np.array(fac_ins.index == ret_ins.index))
    assert np.all(np.array(fac_ins.groupby(fac_ins.index.date).size() == num_minutes))
    assert np.all(np.array(ret_ins.groupby(ret_ins.index.date).size() == num_minutes))

    # process data
    if model_config['window_size'] is not None:
        ret_ins = erase_daily_gaps(ret_ins, model_config['window_size'] - 1)
    mas_ins = create_data_mask(ret_ins)
    ret_ins = normalize_return(ret_ins)
    fac_ins = fill_inf_and_nan(fac_ins)
    ret_ins = fill_inf_and_nan(ret_ins)

    # save model_config
    model_config['num_factors'] = fac_ins.shape[1]
    config_path = os.path.join(home, 'model_config.pkl')
    save_pickle(model_config, config_path)

    # save model_record
    model_record = {
        'factor_list': fac_ins.columns.to_list(),
        'sample_time': fac_ins.index.to_list(),
    }
    record_path = os.path.join(home, 'model_record.pkl')
    save_pickle(model_record, record_path)

    # 5-fold cross-validation
    kf = KFold(n_splits=5, shuffle=True, random_state=random_seed)
    zeros = np.zeros([fac_ins.shape[0] // num_minutes, 100], dtype=np.float)
    for k, (train_dates, valid_dates) in enumerate(kf.split(zeros)):
        # set logger
        log_path = os.path.join(home, 'log.{}.txt'.format(k))
        logger = Logger(file_path=log_path, save_info=save_info, show_info=show_info)

        # split data
        train_index = np.concatenate([np.arange(i * num_minutes, (i + 1) * num_minutes, dtype=np.int) for i in train_dates], axis=0)
        valid_index = np.concatenate([np.arange(i * num_minutes, (i + 1) * num_minutes, dtype=np.int) for i in valid_dates], axis=0)

        fac_train = fac_ins.iloc[train_index]
        fac_valid = fac_ins.iloc[valid_index]
        ret_train = ret_ins.iloc[train_index]
        ret_valid = ret_ins.iloc[valid_index]
        mas_train = mas_ins.iloc[train_index]
        mas_valid = mas_ins.iloc[valid_index]

        # process data
        fac_train_np, ret_train_np, mas_train_np = fac_train.values, ret_train.values, mas_train.values
        fac_valid_np, ret_valid_np, mas_valid_np = fac_valid.values, ret_valid.values, mas_valid.values
        if model_config['objective'] == 'CLA':
            ret_train_np = convert_to_prob(ret_train_np, a=2)
            ret_valid_np = convert_to_prob(ret_valid_np, a=2)

        # set random seed
        set_random_seed(random_seed)

        # create model
        model = Model(model_config, logger)

        # train model
        model.train(fac_train_np, ret_train_np, mas_train_np, fac_valid_np, ret_valid_np, mas_valid_np)

        # save model
        model_path = os.path.join(home, 'model.{}.pkl'.format(k))
        model.save_model(model_path)
    return None


def predict(model_config, factor_base, ticker_type, update_date, return_time, random_seed, prod_version=True, end_date=None):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    start_time = datetime.datetime.now().strftime(fmt)
    print('[{}] predict: {}, {}, {}, {}'.format(start_time, identifier, update_date, return_time, random_seed), flush=True)

    # make directory
    if prod_version:
        home = os.path.join(root, 'model', 'model_prod', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
    else:
        home = os.path.join(root, 'model', 'model_temp', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
    assert os.path.exists(home)

    # prepare data
    factor_path = os.path.join(root, 'data', 'factor', '{}.h5'.format(factor_base))
    fac_all = pd.read_hdf(factor_path)
    assert isinstance(fac_all, pd.DataFrame)

    oos_str_date = (pd.Timestamp(update_date) + pd.Timedelta(days=1)).strftime('%Y%m%d')
    oos_end_date = end_date
    assert pd.Timestamp(oos_str_date) < pd.Timestamp(oos_end_date)
    fac_oos = fac_all.loc[oos_str_date:oos_end_date]

    num_minutes = model_config['num_minutes']
    assert np.all(np.array(fac_oos.groupby(fac_oos.index.date).size() == num_minutes))

    # process data
    fac_oos = fill_inf_and_nan(fac_oos)

    # load model_config
    config_path = os.path.join(home, 'model_config.pkl')
    model_config = load_pickle(config_path)

    # 5-fold cross-validation
    for k in range(5):
        # create model
        model = Model(model_config)

        # load model
        model_path = os.path.join(home, 'model.{}.pkl'.format(k))
        model.load_model(model_path)

        # make prediction
        fac_oos_np = fac_oos.values
        ret_oos_np = model.predict(fac_oos_np)
        ret_oos = pd.Series(ret_oos_np, index=fac_oos.index)

        # save prediction
        prediction_path = os.path.join(home, 'prediction.{}.pkl'.format(k))
        save_pickle(ret_oos, prediction_path)
    return None


def export(model_config, factor_base, ticker_type, update_date, return_time, random_seed, prod_version=True):
    identifier = '{}.{}.{}'.format(model_config['config_name'], factor_base, ticker_type)
    start_time = datetime.datetime.now().strftime(fmt)
    print('[{}] export: {}, {}, {}, {}'.format(start_time, identifier, update_date, return_time, random_seed), flush=True)

    # make directory
    if prod_version:
        home = os.path.join(root, 'model', 'model_prod', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
    else:
        home = os.path.join(root, 'model', 'model_temp', identifier, update_date, 'time_{}'.format(return_time), 'seed_{}'.format(random_seed))
    assert os.path.exists(home)

    # load model_config
    config_path = os.path.join(home, 'model_config.pkl')
    model_config = load_pickle(config_path)

    # 5-fold cross-validation
    for k in range(5):
        # create model
        model = Model(model_config)

        # load model
        model_path = os.path.join(home, 'model.{}.pkl'.format(k))
        model.load_model(model_path)

        # export model
        network = model.network
        network.eval()
        if model_config['window_size'] is None:
            x = torch.randn(1, model_config['num_factors'])
        else:
            x = torch.randn(1, model_config['window_size'], model_config['num_factors'])
        onnx_path = os.path.join(home, 'model.{}.onnx'.format(k))
        torch.onnx.export(network, x, onnx_path)
    return None
