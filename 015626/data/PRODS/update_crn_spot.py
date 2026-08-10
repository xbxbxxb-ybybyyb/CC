
import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'onnx'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'onnxruntime'])



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
from joblib import Parallel, delayed

full_date = '20240628'


flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

model_name_list = ['%s_ic_ic_v7unifac_crn'%full_date, '%s_im_im_v1unifac_crn'%full_date, '%s_if_if_v7_crn'%full_date]

version_list = [(item.split(full_date + '_'))[-1][3:].replace('_new2', '').replace('_new', '') for item in model_name_list]

######## regular setting #######


model_date_dict = {'if_v7c':'%s_if_if_v7c'%full_date,
                   'if_v7_crn':'%s_if_if_v7_crn'%full_date,                  
                   'ic_v7unifac': '%s_ic_ic_v7unifac'%full_date,
                   'ic_v7unifac_crn': '%s_ic_ic_v7unifac_crn'%full_date,
                   'ic_v7unifac_crn_old': '%s_ic_ic_v7unifac_crn_old'%full_date,
                   'ic_v7c': '%s_ic_ic_v7c'%full_date,
                   'im_v1unifac_crn': '%s_im_im_v1unifac_crn'%full_date,  
 }



version_ticker_dict = {'if_v7_crn':'IF.CFE', 'if_v7c':'IF.CFE', 
                       'ic_v7unifac_crn': 'IC.CFE', 'ic_v7unifac': 'IC.CFE', 'ic_v7unifac_crn_old': 'IC.CFE', 
                       'im_v1unifac_crn': 'IM.CFE'}
model_date_use_dict = {
                       'if_v7_crn':'%s'%(model_date_dict['if_v7_crn']),
                       'if_v7c':'%s'%(model_date_dict['if_v7_crn']),
                       'ic_v7unifac_crn':'%s'%(model_date_dict['ic_v7unifac_crn']),
                       'ic_v7unifac_crn_old':'%s'%(model_date_dict['ic_v7unifac_crn_old']),
                       'ic_v7unifac':'%s'%(model_date_dict['ic_v7unifac']),
                       'ic_v7c':'%s'%(model_date_dict['ic_v7c']),
                       'im_v1unifac_crn':'%s'%(model_date_dict['im_v1unifac_crn']),
                       }

_, __, update_date_list = check_update_date()

def calc(ud, model_name):
    # set update date
    update_date = str(ud)
    print('update_date: {}'.format(update_date))

    # set model dir and output dir
    
    model_trade_dir = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_trade/%s'%(model_name, model_name)
    model_value_dir = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value'%model_name

    #assert os.path.exists('{}/model_raw_itr'.format(model_value_dir))
    print('{}/model_raw'.format(model_value_dir))
    assert os.path.exists('{}/model_raw'.format(model_value_dir))
    assert os.path.exists('{}/model_norm'.format(model_value_dir))

    # other configuration
    model_name_list = ['crn_cla', 'crn_reg']
    pred_time_list = [1, 5, 10]
    
    if '_if_' in model_name.lower():
        model_num = 25
        factor_dir_list = [
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm',
        ]
        
    if '_ic_' in model_name.lower():
        model_num = 25
        factor_dir_list = [
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm',
        ]
        
    if '_im_' in model_name.lower():
        model_num = 25
        factor_dir_list = [
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm',
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
            #model_num = model_num_dict[model]
            update_raw_itr(factor_all, model_trade_dir, model_value_dir, update_date, model_name, pred_time, num_models=model_num)

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
        os.makedirs(path)
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
    def read_factors(file_name, factor_dir = factor_dir):
    #for file_name in file_name_list:
        data_path = '{}/{}'.format(factor_dir, file_name)
        factor = pd.DataFrame(pd.read_hdf(data_path))
        return factor
        #factor_list.append(factor)
    #with Pool(24) as pool:
    #    factor_list = pool.map(read_factors, file_name_list)
    factor_list = Parallel(n_jobs= -1)(delayed(read_factors)(file_name) for file_name in file_name_list)
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
    path2 = flag_rootpath + str(date) + '/' + 'im_factors.success' 
    path3 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_if_zscore.success'
    path5 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_im_zscore.success'
    return os.path.exists(path5) and os.path.exists(path3) and os.path.exists(path4)



    
    
for date in update_date_list:
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')
    for model_name in model_name_list:
        calc(date, model_name)


import os
import pickle
import numpy as np
import pandas as pd
from bisect import bisect_left
from multifactor.IO import IO
from multifactor.utility import dt
from multifactor.data.utils import *
import multifactor.utility.dt as udt

initial = False

ticker_list = ['IF', 'IC', 'IM'] 
model_list = [

              '20240628_im_im_v1unifac_crn',
              '20240628_ic_ic_v7unifac_crn',
              '20240628_if_if_v7_crn',

                ]



def rank_index(ticker, date_list, ticker_list = ticker_list):
    
    # sample parameters
    num_samples = 60000
    min_quantile = 0.25
    max_quantile = 0.75

    # set output path
    output_root = f'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/rank_index/{ticker.lower()}_{num_samples}_{int(min_quantile * 100)}_{int(max_quantile * 100)}'
    os.makedirs(output_root, exist_ok=True)

    # **************************************************


    if ticker == 'IM':
        price = get_price_from_market_data_im(ticker)
    else:
        price = get_price_from_market_data(ticker)

    minute_ret = price.groupby(price.index.date).apply(lambda x: x.pct_change(5, fill_method=None).shift(-6))
    minute_std = price.groupby(price.index.date).apply(lambda x: x.pct_change(1, fill_method=None).rolling(30, min_periods=30, center=True).std())

    for sample_date1 in date_list:
        sample_date = str(sample_date1)
        data_end_date = (pd.Timestamp(sample_date) - pd.Timedelta(days=1)).strftime('%Y%m%d')
        index_list = get_index_list(minute_ret, minute_std, data_end_date, num_samples, min_quantile, max_quantile)
        output_path = f'{output_root}/{sample_date}.pkl'
        print(f'save index to {output_path}', flush=True)
        with open(output_path, mode='wb') as file:
            pickle.dump(index_list, file)
    return None


def get_price_from_market_data(ticker):
    univ = IO.read_data(alt='/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    data = IO.read_data(columns=['close'], alt=f'/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/{ticker}_MINUTE.h5')

    index = univ.xs(f'{ticker}.CFE', level=1)['contract_00']
    index.name = 'Ticker'
    price = data['close']

    date_list = price.index.get_level_values(0).date
    index = index.loc[date_list[0]:date_list[-1]]
    index = index.reset_index()
    index['date'] = [x.date() for x in index['dt']]
    index = index.set_index(['date', 'Ticker'])

    price = price.reset_index()
    price['date'] = [x.date() for x in price['dt']]
    price = price.set_index(['date', 'Ticker'])
    price = price.loc[index.index]
    price = price.set_index('dt')
    price = price['close']
    price = price.between_time(start_time='09:30', end_time='14:56')
    return price
    
    
def get_price_from_market_data_im(ticker):
    im_sim_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/future_twap_im_interpolation.h5'
    price_fake = pd.Series(pd.read_hdf(im_sim_path))
    price_fake = price_fake[:'20220721']  # launch date = 20220722
    price_fake = price_fake.between_time(start_time='09:30', end_time='14:56')

    univ = IO.read_data(alt='/data/group/800466/warehouse/prod/MD/MarketData/MD/UNIVERSE/MD_STOCK_INDEX_FUTURES_UNIVERSE.h5')
    data = IO.read_data(columns=['twap'], alt=f'/data/group/800466/warehouse/prod/MD/MarketData/MD/CHINA_FUTURES/MINUTE/backup/{ticker}_MINUTE.h5')

    index = univ.xs(f'{ticker}.CFE', level=1)['contract_00']
    index.name = 'Ticker'
    price_real = data['twap']

    date_list = price_real.index.get_level_values(0).date
    index = index.loc[date_list[0]:date_list[-1]]
    index = index.reset_index()
    index['date'] = [x.date() for x in index['dt']]
    index = index.set_index(['date', 'Ticker'])

    price_real = price_real.reset_index()
    price_real['date'] = [x.date() for x in price_real['dt']]
    price_real = price_real.set_index(['date', 'Ticker'])
    price_real = price_real.loc[index.index]
    price_real = price_real.set_index('dt')
    price_real = price_real['twap']
    price_real = price_real['20220722':]  # launch date = 20220722
    price_real = price_real.between_time(start_time='09:30', end_time='14:56')

    price = pd.concat([price_fake, price_real], axis=0)
    price = price.between_time(start_time='09:30', end_time='14:56')
    return price

def get_index_list(minute_ret, minute_std, data_end_date, num_samples, min_quantile, max_quantile):
    assert len(minute_ret[:data_end_date]) >= num_samples
    assert len(minute_std[:data_end_date]) >= num_samples
    minute_ret = minute_ret[:data_end_date].tail(num_samples)
    minute_std = minute_std[:data_end_date].tail(num_samples)

    min_std = minute_std.quantile(min_quantile)
    max_std = minute_std.quantile(max_quantile)

    select_pos = (minute_ret > 0) & (minute_std > min_std) & (minute_std < max_std)
    select_neg = (minute_ret < 0) & (minute_std > min_std) & (minute_std < max_std)
    select_num = min(select_pos.sum(), select_neg.sum())
    select_pos = select_pos[select_pos].tail(select_num)
    select_neg = select_neg[select_neg].tail(select_num)

    index_list = select_pos.index.to_list() + select_neg.index.to_list()
    index_list.sort()
    return index_list
    
def norm2(model_name, date_list, init = initial):
    print('_______________________________' + model_name + '_______________________________' )
    if '_ic_' in model_name:
        cat = 'ic'
    elif '_if_' in model_name:
        cat = 'if'
    elif '_im_' in model_name:
        cat = 'im'
    
    model_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s'%model_name
    index_root = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/rank_index/%s_60000_25_75'%cat
    
    if init == True:
        for i, date1 in enumerate(date_list):
            date = str(date1)
            if i == 0:
                model_date = model_name.split('_')[0]
                
                initialize_model_norm2(model_date, model_root, index_root)
            else:
                update_model_norm2(date, model_root, index_root)
                
    else:
        for i, date1 in enumerate(date_list):
            date = str(date1)
            update_model_norm2(date, model_root, index_root)
        return None


def initialize_model_norm2(model_date, model_root, index_root):
    output_root = f'{model_root}/model_value/model_norm2/{model_date}'
    os.makedirs(output_root, exist_ok=True)

    pred_comb2 = []
    for model_file in os.listdir(f'{model_root}/model_value/model_raw/{model_date}'):
        model_name, _ = os.path.splitext(model_file)
        print(f'initialize model_norm2: {model_name}')

        # load raw signal
        signal_path = f'{model_root}/model_value/model_raw/{model_date}/{model_name}.pkl'
        signal = pd.read_pickle(signal_path)

        # normalize signal
        signal_list = []
        signal_date_list = pd.to_datetime(signal.index.date).drop_duplicates().strftime('%Y%m%d').to_list()
        for signal_date in signal_date_list:
            signal_temp = signal[signal_date]
            signal_norm = pd.DataFrame(np.full(signal_temp.shape, np.nan), index=signal_temp.index, columns=signal_temp.columns)
            index_path = f'{index_root}/{signal_date}.pkl'
            if not os.path.exists(index_path):
                print(f'[{signal_date}] index file not found: {index_path}')
            else:
                with open(index_path, mode='rb') as file:
                    index_list = pickle.load(file)
                index_diff = pd.to_datetime(index_list).difference(signal.index)
                if len(index_diff) > 0:
                    fmt = '%Y-%m-%d'
                    print(f'[{signal_date}] miss historical value: {len(index_diff)} minutes, from {index_diff[0].strftime(fmt)} to {index_diff[-1].strftime(fmt)}')
                else:
                    print(f'[{signal_date}] done')
                    signal_base = signal[signal.index.isin(index_list)]
                    for col in signal.columns:
                        a = np.sort(signal_base[col].values)
                        signal_norm[col] = [bisect_left(a, x) for x in signal_temp[col].values]
                    signal_norm = signal_norm / len(a) * 2 - 1
            signal_list.append(signal_norm)
        signal_all = pd.concat(signal_list, axis=0)
        pred_comb2.append(signal_all)

        # save signal_all
        output_path = f'{output_root}/{model_name}.pkl'
        print(f'save model norm2 to {output_path}')
        signal_all.to_pickle(output_path)

    # save pred_comb2
    pred_comb2 = pd.concat(pred_comb2, axis=1)
    pred_comb2 = pred_comb2.mean(axis=1)
    output_path = f'{output_root}/pred_comb2.pkl'
    print(f'save model norm2 to {output_path}')
    pred_comb2.to_pickle(output_path)
    return None


def update_model_norm2(update_date, model_root, index_root):
    output_root = f'{model_root}/model_value/model_norm2/{update_date}'
    os.makedirs(output_root, exist_ok=True)
    
    pred_comb2 = []
    for model_file in os.listdir(f'{model_root}/model_value/model_raw/{update_date}'):
        model_name, _ = os.path.splitext(model_file)
        print(f'update model_norm2: {model_name}')

        # load raw signal
        signal_path = f'{model_root}/model_value/model_raw/{update_date}/{model_name}.pkl'
        signal = pd.read_pickle(signal_path)

        # normalize signal
        signal_date = update_date
        signal_temp = signal[signal_date]
        signal_norm = pd.DataFrame(np.full(signal_temp.shape, np.nan), index=signal_temp.index, columns=signal_temp.columns)
        index_path = f'{index_root}/{signal_date}.pkl'
        if not os.path.exists(index_path):
            print(f'[{signal_date}] index file not found: {index_path}')
        else:
            with open(index_path, mode='rb') as file:
                index_list = pickle.load(file)
            index_diff = pd.to_datetime(index_list).difference(signal.index)
            if len(index_diff) > 0:
                fmt = '%Y-%m-%d'
                print(f'[{signal_date}] miss historical value: {len(index_diff)} minutes, from {index_diff[0].strftime(fmt)} to {index_diff[-1].strftime(fmt)}')
            else:
                print(f'[{signal_date}] done')
                signal_base = signal[signal.index.isin(index_list)]
                for col in signal.columns:
                    a = np.sort(signal_base[col].values)
                    signal_norm[col] = [bisect_left(a, x) for x in signal_temp[col].values]
                signal_norm = signal_norm / len(a) * 2 - 1
        signal_new = signal_norm

        # concatenate
        latest_date = None
        date_list = os.listdir(f'{model_root}/model_value/model_norm2')
        date_list = sorted(date_list, reverse=False)
        for date in date_list:
            if date < update_date:
                latest_date = date
        if latest_date is None:
            print('missing historical raw value')
            raise Exception
        signal_path = f'{model_root}/model_value/model_norm2/{latest_date}/{model_name}.pkl'
        signal_old = pd.read_pickle(signal_path)
        signal_all = pd.concat([signal_old, signal_new], axis=0)
        pred_comb2.append(signal_all)

        # save signal_all
        output_path = f'{output_root}/{model_name}.pkl'
        print(f'save model norm2 to {output_path}')
        signal_all.to_pickle(output_path)

    # save pred_comb2
    pred_comb2 = pd.concat(pred_comb2, axis=1)
    pred_comb2 = pred_comb2.mean(axis=1)
    output_path = f'{output_root}/pred_comb2.pkl'
    print(f'save model norm2 to {output_path}')
    pred_comb2.to_pickle(output_path)
    return None

def minute_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'                
    flag_path = flag_rootpath + str(date) + '/'
    path1 = flag_rootpath + str(date) + '/' + 'if_factors.success' 
    path2 = flag_rootpath + str(date) + '/' + 'im_factors.success' 
    path3 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_GEN_MODEL_FACTORS.success'
    path4 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + 'MODEL.success'
    path5 = flag_path + str(date) + '_im_twap.success'
    print(os.path.exists(path1))
    print(os.path.exists(path4))
    print(os.path.exists(path5))
    return os.path.exists(path1) and os.path.exists(path1) and os.path.exists(path4) and os.path.exists(path5)


_,eedate,date_list = check_update_date()
edate = str(eedate)
print(edate)
print('------wait data flag')
while True:
    if minute_flag_check(edate):
        break
    time.sleep(60)
print('flag check finished!')


date_list.append(int(udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')))
for ticker in ticker_list:  
    rank_index(ticker, date_list)
    
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
flag_path_success = flag_rootpath + str(edate) + '/' + 'RANK_INDEX.success'
with open(flag_path_success,'w') as file:
    pass

    for model_name in model_list:
        norm2(model_name, date_list[:-1])

