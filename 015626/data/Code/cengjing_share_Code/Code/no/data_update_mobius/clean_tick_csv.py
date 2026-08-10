from xquant.futuredata import FutureData
from multiprocessing import Pool
import pandas as pd
import numpy as np
import os
import traceback
from function_tools_data import *
from xquant.compute.aimr import AIMR
import time
from multifactor.data.utils import *

#ROOT_PATH = '/arch1/group/800466/MarketData/LOCAL_DATA/CSV/TICK/CHINA_FUTURES/ALL_CONTRACT'
#DEST_PATH = '/arch1/group/800466/MarketData/LOCAL_DATA/TICK'


ROOT_PATH = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/CSV/TICK/CHINA_FUTURES/ALL_CONTRACT'
DEST_PATH = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/TICK'

VARIETY_LIST = ['IC','IF','IH']

def clean_single_day(instrument_id, date):

    folder_name = instrument_id.split('.')[0]
    
    df_tick = pd.read_csv('{}/{}/{}.csv'.format(ROOT_PATH,folder_name,date))

    old_column_names = ['TradingDate', 'dt', 'PreOpenInterest', 'OpenInterest', 'PreClosePx', 'PreSettlePrice',
                        'OpenPx', 'HighPx', 'LowPx', 'LastPx', 'TotalVolumeTrade', 'TotalValueTrade', 'ClosePx',
                        'SettlePrice', 'Buy1Price', 'Buy1OrderQty',
                        'Sell1Price', 'Sell1OrderQty', 'Buy2Price', 'Buy2OrderQty', 'Sell2Price', 'Sell2OrderQty',
                        'Buy3Price', 'Buy3OrderQty', 'Sell3Price', 'Sell3OrderQty', 'Buy4Price', 'Buy4OrderQty',
                        'Sell4Price', 'Sell4OrderQty', 'Buy5Price', 'Buy5OrderQty', 'Sell5Price', 'Sell5OrderQty']

    new_column_names = ['Date', 'Time', 'PreOpenInterest', 'OpenInterest', 'PreClosePx', 'PreSettlePrice', 'OpenPx',
                        'HighPx', 'LowPx', 'LastPx', 'TotalVolumeTrade', 'TotalValueTrade', 'ClosePx',
                        'SettlePrice','BidP0', 'BidV0',
                        'AskP0', 'AskV0', 'BidP1', 'BidV1', 'AskP1', 'AskV1', 'BidP2', 'BidV2', 'AskP2', 'AskV2',
                        'BidP3', 'BidV3', 'AskP3', 'AskV3', 'BidP4', 'BidV4', 'AskP4', 'AskV4']

    df_new_tick = df_tick[old_column_names]

    df_new_tick.columns = new_column_names
    df_new_tick.set_index('Date', inplace=True)

    df_new_tick['Time'] = [int(i.time().strftime('%H%M%S%f')[:-3]) for i in pd.to_datetime(df_new_tick['Time'])]
    df_new_tick['Volume'] = df_new_tick['TotalVolumeTrade'] - df_new_tick['TotalVolumeTrade'].shift(1)
    df_new_tick['Turnover'] = df_new_tick['TotalValueTrade'] - df_new_tick['TotalValueTrade'].shift(1)
    df_new_tick['Interest'] = df_new_tick['OpenInterest'] - df_new_tick['OpenInterest'].shift(1)

    df_new_tick.fillna(0, inplace=True)

    return df_new_tick


def clean_raw_data(start_date, end_date, ncore=20):

    date_list = get_trading_days(start_date, end_date)
    tasks = []

    with Pool(ncore) as pool:

        for date in date_list:
            for variety in VARIETY_LIST:
                instrument_list = FutureData().get_instrument_all(variety, date, date)
                for instrument_id in instrument_list:
                    tasks.append([pool.apply_async(clean_single_day,args=(instrument_id,date,)),instrument_id,date,variety])

        for t,i,d,v in tasks:
            try:
                save_cleaned_data(t.get(),i,d,v)
            except Exception as e:
                print(e, traceback.format_exc())

def save_cleaned_data(df_result, instrument_id, date, variety):
    df_result.to_pickle(get_tick_path(instrument_id, date, variety))
    print('{}_tick_{} is cleaned.'.format(instrument_id, date))

def get_tick_path(instrument_id, date, variety):
    folder_path = check_folder_path(instrument_id, variety)
    return '{}/{}_tick_{}.pickle'.format(folder_path, instrument_id, date)

def check_folder_path(instrument_id, variety):

    #if not os.path.exists('{}/{}'.format(DEST_PATH,variety)):
        #os.mkdir('{}/{}'.format(root_path,variety))

    folder_path = '{}/{}/{}'.format(DEST_PATH,variety,instrument_id)

    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    return folder_path


if __name__ == '__main__':

    #args = AIMR.getParam().split(',')
    #start_date, end_date = '20210922', '20210922'
    
    a, b, c = check_update_date()
    
    flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

    end_date = b
    
    flag_root = flag_rootpath + str(end_date) + '/'
    
    print('wait_minute_flag')
    
    flag_check_path = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(end_date) + '/' + str(end_date)+'_future_tick.success'
    while True:
        if os.path.exists(flag_check_path) == True:
            print('start')
            break
        time.sleep(60)
        
    clean_raw_data(str(c[0]),str(c[-1]))
    
    if not os.path.exists(flag_root):
        os.makedirs(flag_root)

    flag_path_success = flag_root + str(end_date) + '_' + 'clean_tick.success'
    with open(flag_path_success,'w') as file:
        pass