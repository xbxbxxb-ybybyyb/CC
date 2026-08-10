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
               
              '20240329_ic_ic_v7unifac', 
              '20240329_ic_ic_v7unifac_crn',
              '20240329_im_im_v1unifac',
              '20240329_im_im_v1unifac_crn',
              '20240329_if_if_v7c',
              '20240329_if_if_v7_crn'
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
    return os.path.exists(path1) and os.path.exists(path3) and os.path.exists(path4) and os.path.exists(path5)


if __name__ == '__main__':
    
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
        
    for model_name in model_list:
        norm2(model_name, date_list[:-1])


    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'
    flag_path_success = flag_rootpath + str(edate) + '/' + 'NORM2.success'
    with open(flag_path_success,'w') as file:
        pass
