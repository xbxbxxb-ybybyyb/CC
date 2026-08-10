# -*- coding: utf-8 -*-
"""
Created on Tue Aug  7 10:47:51 2018

@author: 012315
"""

import os 
import pandas as pd
import datetime as dt
from multifactor.IO import IO
from multifactor.IO.IO_enums import *


def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def get_latest_list(source_path):
    # accept xls, xlsx 
    file_list = os.listdir(source_path)
    file_list.sort()
    file_path = os.path.join(source_path,file_list[-1])
    print ('getting data from: %s'%(file_path))
    data = pd.read_excel(file_path)
    head_list = data.columns.tolist()
    if '证券代码' in head_list:
        stk_col = '证券代码'
    elif '股票代码' in head_list:
        stk_col = '股票代码'
    stk_list = data[stk_col].apply(ticker_match).values.tolist()
    return stk_list


def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101, 20210101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
    if current_hour < new_date_time and nearest_date == current_date:
        print('Not till refresh time ' + str(new_date_time) + ':00')
        current_date = fdate_list[fdate_list.index(current_date) - 1]
        print('Use previous trading date: ' + str(current_date))
    elif nearest_date < current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date == current_date:
        print('Right on time: ' + str(current_date))
    return current_date


def update_htsc_stock_list(base_path = r'Z:\warehouse\prod\LOCAL_DATA\CSV\stock_universe\HTSC',
                           h5_path=r'Z:\warehouse\prod\univ\CHINA_STOCK\DAILY\HTSC\UNIV_CHINA_STOCK_DAILY_HTSC.h5'):
    
    current_date = get_current_date()
    current_date_dt = dt.datetime.strptime(str(current_date), '%Y%m%d')  

    blacklist_path = os.path.join(base_path,'blacklist')
    # blacklist_group_path = os.path.join(base_path,'blacklist_group')
    blacklist_group_path = 'W:\\chenyx\\blacklist_group\\blacklist_group_daily\\'
    blacklist_exchange_path = os.path.join(base_path,'blacklist_exchange')
    blacklist_ziying_path = os.path.join(base_path,'blacklist_ziying')
    # whitelist_path = os.path.join(base_path,'whitelist')

    whitelist_path = 'W:\\wangwd\\data_file_for_ALPHA\\white_list\\'
    blacklist = get_latest_list(blacklist_path)
    blacklist_group = get_latest_list(blacklist_group_path)
    blacklist_exchange = get_latest_list(blacklist_exchange_path)
    blacklist_ziying = get_latest_list(blacklist_ziying_path)
    # print(blacklist_ziying)
    whitelist = get_latest_list(whitelist_path)
    
    htsc_trade_list = list((set(whitelist) - set(blacklist)) - set(blacklist_group) - set(blacklist_exchange) - set(blacklist_ziying))
    htsc_trade_list.sort()
    index_tuple = [[current_date_dt]*len(htsc_trade_list),htsc_trade_list]
    mi_index = pd.MultiIndex.from_tuples(list(zip(*index_tuple)),names=['dt', 'Ticker'])         
    result_mi = pd.DataFrame([True]*len(htsc_trade_list),columns=['htsc_trade_list'],index=mi_index )

    IO.pd_hdf5_writer(result_mi,h5_path,dataset='htsc_trade_list',append=True)

    return 




update_htsc_stock_list()


#

import os 
import pandas as pd
import datetime as dt
from multifactor.IO import IO
from multifactor.IO.IO_enums import *


def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker


def check_stock_list(excel_path,check_date=None,
                     h5_path=r'Z:\warehouse\prod\univ\CHINA_STOCK\DAILY\HTSC\UNIV_CHINA_STOCK_DAILY_HTSC.h5'):
    
    #excel_path=r'Z:\warehouse\prod\LOCAL_DATA\CSV\stock_universe\HTSC\trade_list\2018_08_06_optimal_wt_turnover_O32.xlsx'
    data = pd.read_excel(excel_path,header=1)
    data['证券代码'] = data['证券代码'].apply(ticker_match)
    trade_list_all = IO.read_data([20180101,20990101],alt=h5_path)
    if check_date is None:
        check_date = trade_list_all.index.get_level_values(0)[-1]
        trade_list_check = trade_list_all.xs(check_date)    
    else:
        check_date = IO.str_date_parser(check_date)
        trade_list_check = trade_list_all.xs(check_date)
    trade_list = trade_list_check[trade_list_check==True].index.tolist()
    
    error_list = list(set(data['证券代码']) - set(trade_list))
    error_list.sort()
    if len(error_list)>0:
        print ('Stocks in Restriction List:%s'%(str(error_list)))
        raise Exception
    return 
