import pickle
from xquant.pyfile import Pyfile
from xquant.factor import FactorData
from xquant.thirdpartydata.marketdata import MarketData
import pickle
import gzip
import pandas as pd
import numpy as np
from xquant.pyfile.ftp import pyfileFTP
import os
import datetime as dt
import zipfile
from xquant.xqutils.xqfile import HDFSFile
from xquant.factordata import FactorData
s = FactorData()
from update_30minute_index import rolling

def download_minute(date):
    root = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/XQuant/'
    ma = MarketData()
    stock_root_path = 'stock/' + str(date)
    start_date = str(date) + '090000'
    end_date = str(date) + '153000'
    # stock_list = xq.hset(xq.PlateType.MARKET,date,xq.MarketType.ALLA)
    # result1 = s.hset('MARKET', str(date), 'ALLA')
    # stock_list = list(result1['stock'])
    
    index_root_path = root  + '/index/' + str(date)

    if not os.path.exists(index_root_path):
        os.makedirs(index_root_path)
    index_list = ['399006.SZ']
    for stock in index_list:
        print(stock)
        df = ma.getKLine4ZTDataFrame(stock, start_date, end_date, 10, 20,True)
        df_xquant = df[['MDTime','OpenPx','HighPx','LowPx','ClosePx','TotalVolumeTrade','TotalValueTrade']]
        df_xquant.columns = ['minute','open','high','low','close','volume','amt']
        df_xquant['minute'] = df_xquant['minute'].apply(lambda x : int(x[:4]))
        df_xquant['Ticker'] = stock
        df_xquant.set_index('minute',inplace=True)
        df_xquant.to_csv(index_root_path+'/' + stock + '.csv')
        
# timelist = [20140801]
# for time in timelist:
    # download_minute(time)

def update_minute_pickle(ticker, date_list, destination_path, operation='append'):
    print('ticker:%s,sdate:%d,edate:%d' % (ticker, date_list[0], date_list[-1]))
    if destination_path.find('stock') > 1:
        pickle_file = destination_path + 'UnAdjstedStockMinute_' + ticker[:-3] + '.pkl'
        isIndex = False
    elif destination_path.find('index') > 1:
        pickle_file = destination_path + 'indexMinute_' + ticker[:-3] + '.pkl'
        isIndex = True
    try:
        dat_new_stk = get_minute_data_raw_v2(ticker, date_list, isIndex)
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
            print('ticker:%s,error: read existing pickle failed' % (ticker))
            dat_exist_stk = dat_new_stk
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
            print('ticker:%s,error: append failed' % (ticker))
            # print ('append error')

        if len(dat_minute_stk) >= len(dat_exist_stk):
            #save_pickle(dat_minute_stk, pickle_file)
            dat_minute_stk.to_pickle(pickle_file,compression='gzip')

        else:
            print('ticker:%s,error: data history deleted - dumping not performed' % (ticker))
            # print ('data history deleted - dumping not performed')
    return
    
def get_minute_data_raw_v2(ticker, date_list, isIndex):
    if isIndex:
        path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/XQuant/index/'
    else:
        path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/XQuant/stock/'

    df_list = []
    for date in date_list:
        csv_path = path + str(date) + '/' + ticker + '.csv'
        df = pd.read_csv(csv_path)
        df['Ticker'] = int(ticker[:-3])
        df['dt'] = date
        df_list.append(df)
    df = pd.concat(df_list)
    df.set_index(['dt', 'Ticker'], inplace=True)
    return df

def update_by_date(sdate=None, edate=None):
    '''
    after minute data update sucessfully,
    make the data by date
    '''
    date_list = [sdate]
    print(date_list)
    root_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/'
    index_path = root_path + 'index/'
    index_dest = root_path + 'index_perdate/'
    for date in date_list:
        index_df_list = []
        for file in os.listdir(index_path):
            if '399001' in file or '399006' in file or '000001' in file:
                continue
            pickle_file = index_path + file
            df = pd.read_pickle(pickle_file,compression='gzip')
            df.reset_index('Ticker', inplace= True)
            df = df.loc[int(date)]
            df.reset_index('dt',inplace=True)
            df.set_index(['dt','Ticker'],inplace=True)
            index_df_list.append(df)
        index_df = pd.concat(index_df_list)
        pickle_file = index_dest + str(date) + '.pkl'
        index_df.to_pickle(pickle_file,compression='gzip')
        print(index_df)
    
# destination_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/index/'
# # ticker_list = ['000001.SH']
# # date_list = [20150410,20150721]
# ticker_list = ['399006.SZ']
# date_list = [20140801]
# for ticker in ticker_list:
    # print(ticker,'*'*20)
    # update_minute_pickle(ticker, date_list, destination_path, operation='append')
# date_list = [20150410,20150721,20140801]
# # for date in date_list:
    # # update_by_date(date,date) 
# for date in date_list:
    # print(date, 'index **********')
    # rolling(date,date)