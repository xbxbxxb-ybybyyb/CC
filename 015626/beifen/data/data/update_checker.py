# -*- coding: utf-8 -*-
"""
Created on Mon Mar  5 08:48:17 2018

@author: 012315
"""

import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import pandas as pd
import datetime as dt
import os
import time


import scipy.io as sio 
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures
import datetime as dt



def get_current_date(new_date_time=18):
    """if current date is not pass new_date_time such as 18 (6pm)
       it will return previous trading day 
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print ('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x:abs(x-current_date) if x<=current_date else 100)
    if current_hour < new_date_time and nearest_date==current_date:
        print ('Not till refresh time '+str(new_date_time)+':00')
        current_date = fdate_list[fdate_list.index(current_date)-1]
        print ('Use previous trading date: '+str(current_date))
    elif nearest_date<current_date:
        current_date = nearest_date
    elif current_hour >= new_date_time and nearest_date==current_date:
        print ('Right on time: '+str(current_date))
    return current_date



def date_period_handler(sdate=None,edate=None):
    last_day = get_current_date()
    if sdate is None and edate is None:
        sdate = last_day
        edate = last_day
        print ('update for one day: '+str(sdate))
    if sdate is not None and edate is None:
        edate = last_day
    else:
        fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
        fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
        cdate_list = [i for i in fdate_list if i<=min(edate,last_day) and i>=sdate]
        sdate,edate = cdate_list[0],cdate_list[-1]
    return sdate,edate


def check_update_date(sdate=None,edate=None,use_len=None):
    #check_update_date(sdate=None,edate=None)
    use_len = 0 if use_len is None else use_len
    sdate,edate = date_period_handler(sdate,edate)
    fdate_list_dt = IO.read_data([20090101,20200101],ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in fdate_list_dt]
    cdate_list = [i for i in fdate_list if i>=sdate and i<=edate]
    idx = max(0,fdate_list.index(cdate_list[0])-use_len)
    sdate_prev = fdate_list[idx]
    print ('-'*20,'\ndata used: %d - %d '%(sdate_prev,edate))
    print ('factor data: %d - %d \ntotal count: %d'%(sdate_prev,edate,len(cdate_list)))
    print ('-'*20)
    return sdate_prev,edate,cdate_list




def read_minute_mat_ultra(file_path):
    id_pos = file_path.rfind('\\')
    fname = file_path[id_pos+1:]
    header_list = ['dt','minute','open','high','low','close','volume','amt']
    dat1 = sio.loadmat(file_path)  
    dat = pd.DataFrame(dat1[fname[:-4]],columns=header_list)
    dat['Ticker'] = int(fname[-10:-4])
    dat['dt'] = dat['dt'].astype('int32')
    dat = dat.set_index(['dt','Ticker'])
    return dat


def slice_minute_data(dat,start_date,end_date):
    dat['date'] = dat.index.get_level_values(0)
    dat['take'] = (dat['date']>=start_date) & (dat['date']<= end_date)
    dat_slice = dat[dat['take']==True].iloc[:,:-2]
    return dat_slice


def check_minute_data(dat):
    dat_count = dat.groupby(['dt','Ticker']).count()['close']
    return dat_count

def calc_wrapper_date(func,file_list,sdate=None,edate=None):
    pm_list = []
    stock_num = len(file_list) if type(file_list)==list else 1
    for i in range(stock_num):
        try:
            if stock_num>1:
                file_path = file_list[i] 
                print (i+1,'/',stock_num,'---',file_path[-10:-4])    
            else:
                file_path = file_list
                
            dat = read_minute_mat_ultra(file_path)
            if sdate is not None:
                dat = slice_minute_data(dat,sdate,edate)            
            stats = func(dat)
            pm_list.append(stats)
        except:
            print ('fail!!!!!!!')
    pm_contain = pd.concat(pm_list,axis=0)
    return pm_contain


def func_parallel_wrap_date(func,input_list,sdate=None,edate=None,max_workers=10):
    # estimation time: 8 min for 3500 stocks
    tic = time.time()
    total_job = len(input_list)
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(calc_wrapper_date,func,file_path,sdate,edate): file_path for file_path in input_list}
        #future_to_file_list = {executor.submit(func, sdate=sdate,edate=edate,stockcode=stockcode):stockcode for stockcode in stocklist}
        list_collector = []
        for future in concurrent.futures.as_completed(future_to_file_list):
            file_path = future_to_file_list[future]
            try:
                data = future.result()
                list_collector.append(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (file_path, exc))
            else:
                print('%d/%d - %r has %d rows' % (input_list.index(file_path)+1,total_job,file_path, len(data)))
        print ('concating results')
        data_collector = pd.concat(list_collector,axis=0)
    toc = time.time()
    print (toc-tic)
    print ('-'*20,' End ','-'*20)
    return data_collector



def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker

def dt_parser(date):
    date_obj = dt.datetime.strptime(str(int(date)),'%Y%m%d')
    return date_obj

def dt_ticker_reformat(dat,dtype='df'):
    if dtype=='mi':
        dat = dat.reset_index()
        dat['Ticker'] = dat['Ticker'].apply(ticker_match)
        dat['dt'] = dat['dt'].apply(dt_parser)
        dat = dat.set_index(['dt','Ticker'])    
    elif dtype=='df':
        dat.columns = [ticker_match(i) for i in dat.columns]
        dat.index = [dt_parser(i) for i in dat.index]
    return dat


def data_checker_minute(sdate=None,edate=None,check_win=None,source_path=None):
    check_win = 5 if check_win is None else check_win
    start_date,end_date,cdate_list = check_update_date(sdate,edate,use_len=check_win)
    source_path = 'S:\\Quant\\StockUnAdjstedMinuteMatData\\' if source_path is None else source_path
    mat_list = [i for i in os.listdir(source_path)]
    file_list = [source_path+i for i in mat_list]
    file_list.sort()
    func = check_minute_data
    check1 = calc_wrapper_date(func,file_list[0],sdate,edate)
    minute_count_MI = func_parallel_wrap_date(check_minute_data,file_list,sdate,edate,max_workers=10)
    minute_count = dt_ticker_reformat(minute_count_MI.unstack())
    minute_status = minute_count.sum(axis=1)/(242*minute_count.shape[1])
    return minute_status


def data_checker(sdate=None,edate=None,check_win=None,minute_check=True):
    check_win = 5 if check_win is None else check_win
    start_date,end_date,cdate_list = check_update_date(sdate,edate,use_len=check_win)
    
    file_path = 'S:\\Quant\\backtest\\local_data\\log_master\\'
    
    # Market Data
    print ('Checkinf H5 file')
    dat_dict = {}
    print ('md')
    dat_dict['md'] = IO.read_data([start_date,end_date],ftype=FType.MD,dsource=DSource.WIND,max_workers=1)
    print ('fdd')
    dat_dict['fdd'] = IO.read_data([start_date,end_date],columns=['pb_lf'],ftype=FType.FDD,dsource=DSource.WIND,dfreq=DFreq.DAILY,max_workers=1)
    # Risk Universe & Alpha Universe
    print ('risk')
    dat_dict['risk'] = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM,columns=['risk_universe'])
    print ('alpha')
    dat_dict['alpha'] = IO.read_data([start_date,end_date],ftype=FType.UNIV,dsource=DSource.OPTM,columns=['alpha_universe'])
    # Style 
    print ('style')
    dat_dict['style'] = IO.read_data([start_date,end_date],ftype=FType.RISK,dsource=DSource.STYLEFACTOR,max_workers=1)
    # Benchmark
    print ('index')
    dat_dict['index'] = IO.read_data([start_date,end_date],['close'],ftype=FType.MD,dtype=DType.INDEX,dsource=DSource.WIND,max_workers=1)
    # Industry
    print ('industry')
    dat_dict['industry'] = IO.read_data([start_date,end_date],ftype=FType.INDUSTRY,dsource=DSource.WIND,columns=['industry3'],max_workers=1) 
    # Fundamental Data - Daily
    print ('risk source')
    risk_source_list = ['tot_assets','tot_liab','tot_non_cur_liab','tot_equity','yoy_tr','yoynetprofit']
    dat_dict['risk_source'] = IO.read_data([start_date,end_date],risk_source_list,ftype=FType.FDD,dfreq=DFreq.DAILY,dsource=DSource.WIND,max_workers=1)
    # Consensus Forecast - Basic Table
    print ('con_forecast')
    dat_dict['con_forecast'] = IO.read_data([start_date,end_date],ftype=FType.FCD,dsource=DSource.HTSC,max_workers=1)
    # Consensus Forecast - Target Price
    #h5_path_cfs = 'S:\\Quant\\data\\fcd\\CHINA_STOCK\\DAILY\\HTSC\\con_forecast_schedule.h5'
    # Conforecast Deriv Table
    #h5_path_so3 = 'S:\\Quant\\data\\fcd\\CHINA_STOCK\\DAILY\\HTSC\\stock_order3.h5'
    #h5_path_so2 = 'S:\\Quant\\data\\fcd\\CHINA_STOCK\\DAILY\\HTSC\\stock_order2.h5'
    # HTSC stock list
    #h5_trade_list = 'S:\\Quant\\backtest\\local_data\\stock_universe\\HTSC_trade_list.h5'
    #dat_trade = IO.read_data([20090101,20200205],alt=h5_trade_list)

    check_status = {}
    for fac in dat_dict:
        try:
            if fac=='con_forecast':
                check_status[fac] = np.isfinite(dat_dict[fac][['EPS','PB']]).groupby('dt').sum()
            else:    
                check_status[fac] = np.isfinite(dat_dict[fac]).groupby('dt').sum()
        except:
            print(fac)
            
    if minute_check:
        check_status['minute']= data_checker_minute(sdate,edate,check_win)
        
        
    # Minute Data
    """record fail
    print (check_status)
    for fac in check_status:
    check_status[fac] = check_status[fac].to_dict('list') 
    log_file = file_path+str(fdate_list[-1])+'.json'
    with open(log_file, 'w') as f:
        json.dump(check_status, f)
    """
    
    now=dt.datetime.today()
    file_date=now.strftime("%Y%m%d_%H%M%S")    
    excel_name = file_path+str(cdate_list[-1])+'_check_time_'+file_date+'.xlsx'
    writer = pd.ExcelWriter(excel_name,engine='xlsxwriter')
    for fac in check_status:
        check_status[fac].to_excel(writer,sheet_name=fac)
    writer.save()
    print ('Check status saved in: ',excel_name)
    return     




data_checker(minute_check=False)






