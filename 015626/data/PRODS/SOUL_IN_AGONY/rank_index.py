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

ticker_list = ['IM'] 
model_list = ['20230331_im_im_v1unifac_crn']



def rank_index(ticker, date_list, ticker_list = ticker_list):
    
    # sample parameters
    num_samples = 60000
    min_quantile = 0.25
    max_quantile = 0.75

    # set output path
    output_root = f'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/rank_index/{ticker.lower()}_{num_samples}_{int(min_quantile * 100)}_{int(max_quantile * 100)}'
    os.makedirs(output_root, exist_ok=True)

    # **************************************************

    for ticker in ticker_list:
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
    


def minute_flag_check(date):
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'                
    path1 = flag_rootpath + str(date) + '/' + 'if_factors.success' 
    path2 = flag_rootpath + str(date) + '/' + 'im_factors.success' 
    path3 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_GEN_MODEL_FACTORS.success'
    path4 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + 'MODEL.success'
    return os.path.exists(path1) and os.path.exists(path3) and os.path.exists(path4)


if __name__ == '__main__':
    
    _,eedate,date_list = check_update_date(20210101, 20230518)
    edate = str(eedate)
    print(edate)


    date_list.append(int(udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')))
    for ticker in ticker_list:  
        rank_index(ticker, date_list)
        


 
