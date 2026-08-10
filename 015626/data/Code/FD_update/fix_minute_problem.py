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

from update_30minute_vwap import update_30minute_vwap
from update_30minute_index import update_30minute_index

def download_minute(date):
    root = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/XQuant/'
    ma = MarketData()
    stock_root_path = 'stock/' + str(date)
    start_date = str(date) + '090000'
    end_date = str(date) + '153000'
    # stock_list = xq.hset(xq.PlateType.MARKET,date,xq.MarketType.ALLA)
    result1 = s.hset('MARKET', str(date), 'ALLA')
    stock_list = list(result1['stock'])
    
    stock_root_path = root +'/stock/'+str(date)

    if not os.path.exists(stock_root_path):
        os.makedirs(stock_root_path)

    for stock in stock_list:
        print(stock)
        df = ma.getKLine4ZTDataFrame(stock, start_date, end_date, 10, 20, True)
        df_xquant = df[['MDTime','OpenPx','HighPx','LowPx','ClosePx','TotalVolumeTrade','TotalValueTrade']]
        df_xquant.columns = ['minute','open','high','low','close','volume','amt']
        df_xquant['minute'] = df_xquant['minute'].apply(lambda x : int(x[:4]))
        df_xquant['Ticker'] = stock
        df_xquant.set_index('minute',inplace=True)
        df_xquant.to_csv(stock_root_path+'/' + stock + '.csv')

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
    
    
def update_by_date(sdate=None, edate=None):
    '''
    after minute data update sucessfully,
    make the data by date
    '''
    date_list = [sdate]
    print(date_list)
    root_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/'
    

    stock_path = root_path + 'stock/'
    stock_dest = root_path + 'stock_perdate/'
    for date in date_list:
        stk_df = pd.DataFrame()
        for file in os.listdir(stock_path):
            pickle_file = stock_path + file
            print(sdate, pickle_file)
            df = pd.read_pickle(pickle_file,compression='gzip')
            df.reset_index('Ticker', inplace= True)
            try:
                df = df.loc[int(date)]
                df.reset_index('dt',inplace=True)
                df.set_index(['dt','Ticker'],inplace=True)
                if len(stk_df) == 0:
                    stk_df = df
                else:
                    stk_df = pd.concat([stk_df,df])
                print(stk_df)
                # stk_df_list.append(df)
            except Exception as e:
                print(e)
                continue
        pickle_file = stock_dest + str(date) + '.pkl'
        stk_df.to_pickle(pickle_file,compression='gzip')
        print(stk_df)
        
destination_path = '/data/group/800080/warehouse/prod/LOCAL_DATA/CSV/WIND/MINUTE/stock/'                    
ticker_list = ['000009.SZ', '000006.SZ', '000008.SZ', '000007.SZ']
date_list1 = [20160120, 20160229, 20160301, 20160303, 20160304, 20160405, 20160406, 20160411, 20160412, 20160413, 
            20160427, 20160428, 20160429, 20160503, 20160504, 20160505, 20160506, 20160707, 20160708, 20161122, 20161123, 20170601, 
            20170602, 20170605, 20170606, 20170607, 20170608, 20170609, 20170615, 20170616, 20170816, 20170817, 20180917, 20180918]

date_list2 = [20150303, 20150304, 20150305, 20150605, 20150608, 20150722, 20150723, 20150724, 20150806, 20150807, 20160104, 
            20160105, 20160119, 20160120, 20160229, 20160301, 20160303, 20160304, 20160405, 20160406, 20160411, 20160412, 20160413, 
            20160427, 20160428, 20160429, 20160503, 20160504, 20160505, 20160506, 20160707, 20160708, 20161122, 20161123, 20170601, 
            20170602, 20170605, 20170606, 20170607, 20170608, 20170609, 20170615, 20170616, 20170816, 20170817, 20180917, 20180918]
            
date_list = [20170608, 20170609, 20170615, 20170616, 20170816, 20170817, 20180917, 20180918]

# for ticker in ticker_list:
    # print('ticker','*'*20)
    # update_minute_pickle(ticker, date_list, destination_path, operation='append')

# for date in date_list1:
    # update_by_date(date,date)    

# for date in date_list:
    # print(date, 'index **********')
    # update_30minute_index(date,date)



for date in date_list:    
    print(date, 'stock **********')
    update_30minute_vwap(date,date)
        
        
    
print('finish!') 