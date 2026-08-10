# -*- coding: utf-8 -*-
"""
Created on Fri May 18 10:56:19 2018

@author: 012315
"""

from WindPy import w
import datetime as dt
import pandas as pd
import os
import numpy as np
import scipy.io as sio
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import time
import logging
from multifactor.data.utils import *

#import config_reader
#from log import Log
#logger = Log('WIND_MINUTE')

current_time_fmt = dt.datetime.now().strftime('%Y%m%d_%H%M%S')
log_level='INFO'
#log_file='S:\\Quant\\backtest\\local_data\\wind_minute\\log\\wind_minute_update_'+current_time_fmt+'.log'
log_file = 'Z:\\warehouse\\prod\\LOCAL_DATA\\LOG\\WIND\\MINUTE\\wind_minute_update_'+current_time_fmt+'.log'
logger=logging.getLogger('wind_minute_update')
logger.setLevel(eval('logging.'+log_level.upper()))
file_handler=logging.FileHandler(log_file)
file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(file_handler)
logger.info('start minute data update')

w.start()


def get_minute_data_raw(ticker_list, sdate, edate):
    # from WindPy import w
    # w.start()
    fac_list = ['open', 'high', 'low', 'close', 'volume', 'amt']
    minute_start, minute_end = '09:00:00', ' 15:30:00'
    dat = w.wsi(ticker_list, fac_list, str(sdate) + minute_start, str(edate) + minute_end)
    if dat.Data[0][0] == 'CWSSService: quota exceeded.':
        print(dat.Data[0][0])
        raise AssertionError
    df = pd.DataFrame(dat.Data, index=fac_list).T
    df['dt'] = [int(i.strftime('%Y%m%d')) for i in dat.Times]
    df['minute'] = [int(i.strftime('%H%M')) for i in dat.Times]
    df['Ticker'] = int(dat.Codes[0][:-3])
    df = df.set_index(['dt', 'Ticker'])
    df = df[['minute'] + fac_list]
    return df

def get_minute_data_from_xquant(ticker,index=False):
    if index:
        path = 'D:\\013160\\xquant_data\\minute\\index\\'
    else:
        path = 'D:\\013160\\xquant_data\\minute\\stock\\'
    path = path + ticker + '.csv'
    df_quant = pd.read_csv(path, header=0)
    df_quant['dt'] = 20180626
    df_quant['Ticker'] = int(ticker[:-3])
    df_quant.set_index(['dt','Ticker'], inplace=True)
    return df_quant



def update_minute_pickle(ticker, sdate, edate, destination_path, operation='append'):
    logger.info('ticker:%s,sdate:%d,edate:%d' % (ticker, sdate, edate))
    if destination_path.find('stock') > 1:
        pickle_file = destination_path + 'UnAdjstedStockMinute_' + ticker[:-3] + '.pkl'
    elif destination_path.find('index') > 1:
        pickle_file = destination_path + 'indexMinute_' + ticker[:-3] + '.pkl'
    try:
        dat_new_stk = get_minute_data_raw(ticker, sdate, edate)
    except:
        print('wind download error')

    if operation == 'create':
        #save_pickle(dat_new_stk, pickle_file)
        dat_new_stk.to_pickle(pickle_file,compression='gzip')
    elif operation == 'append':
        try:
            #dat_exist_stk = read_pickle(pickle_file)
            dat_exist_stk = pd.read_pickle(pickle_file,compression='gzip')
        except:
            logger.error('ticker:%s,error: read existing pickle failed' % (ticker))
            # print ('read existing pickle error')
        try:
            # check date list
            new_date_list = set(dat_new_stk.index.get_level_values(0))
            date_list = set(dat_exist_stk.index.get_level_values(0))
            duplicate_list = list(date_list.intersection(new_date_list))
            if len(duplicate_list) > 0:
                print('date duplicate & drop:', str(duplicate_list))
                dat_exist_stk = dat_exist_stk.drop(duplicate_list, level=0)
            dat_minute_stk = dat_exist_stk.append(dat_new_stk)
            dat_minute_stk = dat_minute_stk.sort_index(level=0)
        except:
            logger.error('ticker:%s,error: append failed' % (ticker))
            # print ('append error')

        if len(dat_minute_stk) >= len(dat_exist_stk):
            #save_pickle(dat_minute_stk, pickle_file)
            dat_minute_stk.to_pickle(pickle_file,compression='gzip')

        else:
            logger.error('ticker:%s,error: data history deleted - dumping not performed' % (ticker))
            # print ('data history deleted - dumping not performed')
    return


def parallel_io(func, ticker_list, *args, sdate=None, edate=None, max_workers=5, **kwargs):
    tic = time.time()
    total_job = len(ticker_list)
    print('-' * 20, ' Start ', '-' * 20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func, ticker, *args, sdate=sdate, edate=edate, **kwargs): ticker for
                               ticker in ticker_list}
        for future in concurrent.futures.as_completed(future_to_file_list):
            ticker = future_to_file_list[future]
            try:
                future.result()
            except Exception as exc:
                print('%r generated an exception: %s' % (ticker, exc))
            else:
                print('%d/%d - %r' % (ticker_list.index(ticker) + 1, total_job, ticker))
    toc = time.time()
    print(toc - tic)
    print('-' * 20, ' End ', '-' * 20)
    return


def get_stock_list(edate):
    dat = w.wset("sectorconstituent", "date=" + str(edate) + ";sectorid=a001010100000000")
    if dat.Data[0][0] == 'CWSSService: quota exceeded.':
        print(dat.Data[0][0])
        raise AssertionError
    stock_list = dat.Data[1]
    return stock_list


def update_wind_minute(sdate=None, edate=None, use_len=5, operation='append'):
    destination_path = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\'
    #destination_path = config_reader.getConfig('root_path', 'wind_minute_path')
    tic = time.time()
    # assume update for last week - 5 days
    logger.info('start downloading minute data' + '-' * 10)
    sdate, edate, cdate_list = check_update_date(sdate=sdate, edate=edate, use_len=use_len)
    logger.info('sdate:%d,edate:%d' % (sdate, edate))
    destination_stk = destination_path + 'stock\\'
    destination_index = destination_path + 'index\\'
    if not os.path.exists(destination_stk):
        os.makedirs(destination_stk)
    if not os.path.exists(destination_index):
        os.makedirs(destination_index)
    logger.info('destination_stk:%s, destination_index:%s' % (destination_stk, destination_index))
    index_list = ['000300.SH', '000905.SH', '000906.SH', '000016.SH']

    print('get ticker list')
    ticker_list = get_stock_list(edate)
    ticker_list.sort()
    logger.info('stock number:%d' % (len(ticker_list)))

    print('update stock minute')
    parallel_io(update_minute_pickle, ticker_list, sdate=sdate, edate=edate, max_workers=5,
                destination_path=destination_stk, operation=operation)
    logger.info('stock download complete')

    print('update index minute')
    parallel_io(update_minute_pickle, index_list, sdate=sdate, edate=edate, destination_path=destination_index,
                operation=operation)
    logger.info('index download complete')
    logger.info('all complete') 
    toc = time.time()
    time_spend = round(toc - tic, 2)
    logger.info('total time:%d' % (time_spend))
    return


if __name__ == '__main__':
    update_wind_minute(use_len=3, operation='append')
    
    
    
    
    
