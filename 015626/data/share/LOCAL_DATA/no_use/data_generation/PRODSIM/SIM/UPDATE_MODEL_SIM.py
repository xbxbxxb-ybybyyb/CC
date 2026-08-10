
import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'onnx'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'onnxruntime'])

import onnx
import onnxruntime as ort

import os
import pickle
import numpy as np
import pandas as pd
import bottleneck as bk
import onnx
import onnxruntime as ort
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS_sim/'

model_name_list = ['20221125_if_if_v7_crn', '20221125_ic_ic_v7uni_crn']

_, __, update_date_list = check_update_date()

def calc(ud, model_name):
    # set update date
    update_date = str(ud)
    print('update_date: {}'.format(update_date))

    # set model dir and output dir
    
    model_trade_dir = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_trade/%s'%(model_name, model_name)
    model_value_dir = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value'%model_name

    assert os.path.exists('{}/model_raw_itr'.format(model_value_dir))
    assert os.path.exists('{}/model_raw'.format(model_value_dir))
    assert os.path.exists('{}/model_norm'.format(model_value_dir))

    # other configuration
    model_name_list = ['crn_cla', 'crn_reg']
    pred_time_list = [1, 5, 10]
    
    if 'if' in model_name.lower():
        factor_dir_list = [
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm',
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm',
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm',
        ]
    if 'ic' in model_name.lower():
        
        factor_dir_list = [
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm',
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm',
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm',
            '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm'    
            
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_prod_v7_2/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_diff_zscore/minute_norm',

        ]
        
    # load data
    str_date = (pd.Timestamp(update_date) - pd.Timedelta(15, 'day')).strftime('%Y%m%d')
    end_date = update_date
    factor_list = []
    for factor_dir in factor_dir_list:
        print('fetch factor from {}'.format(factor_dir))
        factor_all = fetch_factor(factor_dir)
        factor_all = factor_all[str_date:end_date]
        factor_list.append(factor_all)
    factor_all = merge_factor(factor_list)
    factor_all = fill_inf_and_nan(factor_all)

    # calculate new value
    for model_name in model_name_list:
        for pred_time in pred_time_list:
            update_raw_itr(factor_all, model_trade_dir, model_value_dir, update_date, model_name, pred_time, num_models=25)

    # update raw value
    for model_name in model_name_list:
        update_raw(model_value_dir, update_date, model_name, pred_time_list)

    # update norm value
    for model_name in model_name_list:
        update_norm(model_value_dir, update_date, model_name, rank_period=4800)
    
    holder = pd.DataFrame()
    for model_name in model_name_list:
        temp = pd.read_pickle('{}/model_norm/{}/{}.pkl'.format(model_value_dir, update_date, model_name))
        holder = pd.concat([holder, temp], axis = 1)
    ts_rank(holder.mean(axis = 1), 2400).to_pickle('{}/model_norm/{}/{}.pkl'.format(model_value_dir, update_date, 'pred_comb2'))   
    return None


def update_raw_itr(factor_all, model_trade_dir, model_value_dir, update_date, model_name, pred_time, num_models):
    # make prediction
    prediction_all = {}
    for model_idx in range(num_models):
        # load model
        model_path = '{}/{}/{}_{}_{}.onnx'.format(model_trade_dir, model_name, model_name, pred_time, model_idx)
        model_onnx = onnx.load(model_path)
        onnx.checker.check_model(model_onnx)
        model_onnx = model_onnx.SerializeToString()
        ort_sess = ort.InferenceSession(model_onnx)

        # load input list
        input_path = '{}/{}/{}_{}_{}.csv'.format(model_trade_dir, model_name, model_name, pred_time, model_idx)
        input_list = pd.read_csv(input_path)
        input_list = input_list['factor_name'].to_list()

        # prepare model input
        x_pd = factor_all[input_list]
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

        # predict
        y_np = []
        for t in range(pred_input.shape[0]):
            x_np = pred_input[t:t + 1]
            res = ort_sess.run(None, {ort_sess.get_inputs()[0].name: x_np.astype(np.float32)})
            y_np.append(res[0])
        y_np = np.concatenate(y_np, axis=0)
        y_pd = pd.Series(y_np, index=pred_index)

        prediction_all[model_idx] = y_pd[update_date:update_date]
    prediction_all = pd.DataFrame(prediction_all)

    # save prediction
    make_dir('{}/model_raw_itr/{}'.format(model_value_dir, update_date))
    pred_path = '{}/model_raw_itr/{}/{}_{}.pkl'.format(model_value_dir, update_date, model_name, pred_time)
    print('save prediction to {}'.format(pred_path))
    save_pickle(prediction_all, pred_path)
    return None


def update_raw(model_value_dir, update_date, model_name, pred_time_list):
    # average
    pred_new = {}
    for pred_time in pred_time_list:
        pred_path = '{}/model_raw_itr/{}/{}_{}.pkl'.format(model_value_dir, update_date, model_name, pred_time)
        pred_all = load_pickle(pred_path)
        pred_avg = pred_all.mean(axis=1)
        pred_new['{}_{}'.format(model_name, pred_time)] = pred_avg
    pred_new = pd.DataFrame(pred_new)

    # concatenate
    latest_date = None
    date_list = os.listdir('{}/model_raw'.format(model_value_dir))
    date_list = sorted(date_list, reverse=False)
    for date in date_list:
        if date < update_date:
            latest_date = date
    if latest_date is None:
        print('missing historical raw value')
        raise Exception
    print('latest_date: {}, update_date: {}'.format(latest_date, update_date))
    pred_path = '{}/model_raw/{}/{}.pkl'.format(model_value_dir, latest_date, model_name)
    pred_old = load_pickle(pred_path)
    pred_cat = pd.concat([pred_old, pred_new], axis=0)

    # save
    make_dir('{}/model_raw/{}'.format(model_value_dir, update_date))
    pred_path = '{}/model_raw/{}/{}.pkl'.format(model_value_dir, update_date, model_name)
    print('save raw value to {}'.format(pred_path))
    save_pickle(pred_cat, pred_path)
    return None


def update_norm(model_value_dir, update_date, model_name, rank_period):
    # raw value
    signal_path = '{}/model_raw/{}/{}.pkl'.format(model_value_dir, update_date, model_name)
    signal_raw = load_pickle(signal_path)

    # norm value
    signal_norm = ts_rank(signal_raw, rank_period)
    signal_norm_avg = signal_norm.mean(axis=1)
    signal_norm_avg = pd.DataFrame(signal_norm_avg, columns=[model_name])

    # save
    make_dir('{}/model_norm/{}'.format(model_value_dir, update_date))
    signal_path = '{}/model_norm/{}/{}.pkl'.format(model_value_dir, update_date, model_name)
    print('save norm value to {}'.format(signal_path))
    save_pickle(signal_norm_avg, signal_path)
    return None


def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return None


def save_pickle(data, path):
    with open(path, mode='wb') as file:
        pickle.dump(data, file, protocol=3)
    return None


def load_pickle(path):
    with open(path, mode='rb') as file:
        data = pickle.load(file)
    return data


def fetch_factor(factor_dir):
    factor_list = []
    file_name_list = os.listdir(factor_dir)
    for file_name in file_name_list:
        data_path = '{}/{}'.format(factor_dir, file_name)
        factor = pd.DataFrame(pd.read_hdf(data_path))
        factor_list.append(factor)
    factor_all = pd.concat(factor_list, axis=1, join='outer')
    # sort by factor name
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique
    # check time: 09:30 ~ 11:29, 13:00 ~ 14:56, 120 + 117 = 237
    factor_all = factor_all.between_time(start_time='09:30', end_time='14:56')
    assert factor_all.shape[0] % 237 == 0
    return factor_all


def merge_factor(factor_list):
    factor_all = pd.concat(factor_list, axis=1, join='outer')
    # sort by factor name
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique
    # check time: 09:30 ~ 11:29, 13:00 ~ 14:56, 120 + 117 = 237
    factor_all = factor_all.between_time(start_time='09:30', end_time='14:56')
    assert factor_all.shape[0] % 237 == 0
    return factor_all


def fill_inf_and_nan(x):
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.fillna(0.0)
    return x


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

def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + 'if_factors.success' 
    path2 = flag_rootpath + str(date) + '/' + 'ih_factors.success' 
    path3 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_if_zscore.success'
    return os.path.exists(path1) and os.path.exists(path3) and os.path.exists(path4)

if __name__ == '__main__':
    
    
    for date in update_date_list:
        while True:
            if minute_flag_check(date):
                break
            time.sleep(60)
        print('flag check finished!')
        for model_name in model_name_list:
            calc(date, model_name)
        
    flag_path_success = flag_rootpath + str(date) + '/' + 'MODEL.success'
    with open(flag_path_success,'w') as file:
        pass
