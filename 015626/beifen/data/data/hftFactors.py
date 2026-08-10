# -*- coding: utf-8 -*-
"""
Created on Wed Nov 28 19:15:30 2018

@author: 012246
"""

import time
#time.sleep(3600*4)

# import gc
import pandas
# import requests
import time
import numpy as np
# from uqer import DataAPI
from pandas import Series,DataFrame
import pandas as pd
#from datetime import datetime
import datetime
import os
# from multifactor.IO import IO
# from multifactor.IO.IO_enums import *
# from multifactor.backtest import FactorTest
# from multifactor.backtest import FactorTool
# from multifactor.preprocessing import neutralization
# from multifactor.utility import dt
# import multifactor.utility.dt as tdt
import pickle
# from multifactor.ReturnModel import newFactorReturnPick3
# from multifactor.ReturnModel import maxICIR
# import logging
# import xlrd,xlwt
# from xlutils.copy import copy
# from multifactor.ReturnModel import factor_sharp3
# from multifactor.ReturnModel import factor_gather1
# import scipy.io as sio
# from sklearn.model_selection import train_test_split
# from sklearn.naive_bayes import GaussianNB
# import matplotlib.pyplot as plt
# from concurrent.futures import ThreadPoolExecutor
# import concurrent.futures
# from multifactor.utility import common

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
            if file_path.find('.pkl')>0:
                dat = pd.read_pickle(file_path,compression='gzip')
            elif file_path.find('.mat')>0:
                dat = read_minute_mat_ultra(file_path)
            else:
                print('file format not accpetted: %s'%(file_path))
            if sdate is not None:
                sdate=int(IO.str_date_parser(sdate).strftime('%Y%m%d'))
                edate = int(IO.str_date_parser(edate).strftime('%Y%m%d'))
                dat = slice_minute_data(dat,sdate,edate)
            
            stats = func(dat)
            pm_list.append(stats)
        except(Exception,BaseException) as e:
            print(e)
            print ('fail!!!!!!!')
    pm_contain = pd.concat(pm_list,axis=0)
    return pm_contain

def create_m(dts,p):
    #start_k=dts.iloc[[1],:]
    dts=dts.iloc[1:-1,:]
    n=dts.shape[0]
    n=n-n%p
    dts=dts.iloc[:n,:]
    open_new=pd.DataFrame(np.array(dts.loc[:,['open']]).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.iloc[0],axis=1)
    close_new = pd.DataFrame(np.array(dts.loc[:,['close']]).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.iloc[-1],axis=1)
    high_new = pd.DataFrame(np.array(dts.loc[:,['high']]).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.max(),axis=1)
    low_new = pd.DataFrame(np.array(dts.loc[:,['low']]).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.min(),axis=1)
    volume_new = pd.DataFrame(np.array(dts.loc[:,['volume']]).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.sum(),axis=1)
    amt_new = pd.DataFrame(np.array(dts.loc[:,['amt']]).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.sum(),axis=1)
    index_new=pd.DataFrame(np.array(dts.index).reshape(int(dts.shape[0]/p),5)).apply(lambda x:x.iloc[-1],axis=1)
    dts_new=pd.concat([open_new,close_new,high_new,low_new,volume_new,amt_new],axis=1)
    dts_new['Ticker']=dts.loc[:,'Ticker'].iloc[0]
    dts_new.columns=['open','close','high','low','volume','amt','Ticker']
    dts_new=dts_new[['Ticker','open','close','high','low','volume','amt']]
    dts_new.index=index_new
    #dts_new=pd.concat([start_k,dts_new])
    return dts_new

def slice_minute_data(dat,start_date,end_date):
    dat['date'] = dat.index.get_level_values(0)
    dat['take'] = (dat['date']>=start_date) & (dat['date']<= end_date)
    dat_slice = dat[dat['take']==True].iloc[:,:-2]
    return dat_slice

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
def func_parallel_wrap_date(func,input_list,sdate=None,edate=None,max_workers=10,axis=0):
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
        data_collector = pd.concat(list_collector,axis=axis)
    toc = time.time()
    print (toc-tic)
    print ('-'*20,' End ','-'*20)
    return data_collector
def get_minute_bucket(minute_duration,include_1500=True):
    if minute_duration in [1,3,5,10,15,30]:
        minute_list_raw = [i for i in range (930,1501) if (i%100<60 and int(i/100) in [9,10,11,13,14,15])]  
        minute_list = [i for i in minute_list_raw if not (i<1300 and i>1130)]
        minute_am = np.array(minute_list[:121])
        minute_pm = np.array(minute_list[121:])
        seg_idx = [i for i in range(0,120,minute_duration)]
        seg_break = np.append(minute_am[seg_idx],minute_pm[seg_idx])
        seg = [[i,i+minute_duration-1] for i in seg_break] 
    elif minute_duration == 20:
        seg = [[930,949],[950,1009],[1010, 1029],[1030,1049],[1050,1109],[1110,1129],[1300, 1319],
               [1320,1339],[1340,1359],[1400,1419],[1420,1439],[1440,1459]]
    elif minute_duration == 60:
        seg = [[930,1029],[1030,1129],[1300,1359],[1400,1459]]
    elif minute_duration == 120:
        seg = [[930,1129],[1300,1459]]
    elif minute_duration == 240:
        seg = [[930,1129],[1300,1459]]
    else:
        print ('not defined...')
        seg = []      
    if include_1500 and seg[-1][-1]==1459:
        seg[-1][-1]=1500
    return seg 


def calc_minute_ret_block(dat,minute_duration=30):
    dat['block'] = get_minute_seg(dat['minute'],minute_duration)
    dat['ret'] = calc_minute_ret(dat)
    dat_grp_block = dat.groupby(['dt','Ticker','block'])
    dat_ret = dat_grp_block[['ret']].sum()
    return dat_ret


def get_minute_seg(minute_num,minute_duration):
    # 925:bidding / 930: 930-931  / ignore 1500
    #seg = get_minute_bucket(minute_duration=30)
    #seg_raw = [[minute2raw(j) for j in i] for i in seg]
    minute_mat = minute_num.values
    #minute_block = np.array([np.nan]*len(minute_num))
    minute_block = np.zeros(len(minute_num))
    minute_block[:] = np.nan
    minute_type = 'raw' if minute_mat[0:2].mean()>2000 else 'process'
    seg_num = int(240/minute_duration)
    if minute_type=='raw':
      seg1 = get_minute_bucket(minute_duration)
      seg = [[minute2raw(j) for j in i] for i in seg1]
    elif minute_type=='process':
        seg = get_minute_bucket(minute_duration)
    for i in range(seg_num):
        minute_block[(minute_mat>=seg[i][0]) & (minute_mat<=seg[i][1])] = i+1
    return minute_block 

def calc_minute_ret(dat):
    close2close = (dat['close']/dat['close'].shift(1)-1).values
    open2close = (dat['close']/dat['open']-1).values
    mask_open_bid_1st_minute = (dat['minute']<=34200).values  # 33900 / 34200
    close2close[mask_open_bid_1st_minute] = open2close[mask_open_bid_1st_minute]
    return close2close

def get_minute_block(dat,minute_duration):
    dat['block'] = get_minute_seg(dat['minute'], minute_duration)
    dat_grp_block = dat.groupby(['dt', 'Ticker', 'block'])
    close = dat_grp_block[['close']].apply(lambda x:x.iloc[-1])
    open_ = dat_grp_block[['open']].apply(lambda x: x.iloc[0])
    high = dat_grp_block[['high']].apply(lambda x: x.max())
    low = dat_grp_block[['low']].apply(lambda x: x.min())
    volume = dat_grp_block[['volume']].sum()
    amt = dat_grp_block[['amt']].sum()
    minute=dat_grp_block[['minute']].apply(lambda x:x.iloc[-1])
    block=pd.concat([minute,open_,close,high,low,volume,amt],axis=1)
    block.rename(columns={'block':'minute'},inplace=True)
    block=block.reset_index()
    block=block.set_index(['dt','Ticker'])
    return block
#pd.read_pickle('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock\\UnAdjstedStockMinute_000001.pkl')
if  __name__=='__main__':
    root = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock\\'
    dest = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock_5minutes\\'
    exist_list = os.listdir(dest)
    for file in os.listdir(root):
        print(file)
        if file in exist_list:
            print('already exist, continue')
            continue
        pickle_file = root + file
        dat = pd.read_pickle(pickle_file,compression='gzip')
        df = get_minute_block(dat,5)
        print(df)
        df.to_pickle(dest + file, compression='gzip')







    # file_list=common.get_recursive_file('Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock\\',suffix='pkl')
    # start_date='20130101'
    # end_date='20181224'
    # def test_func(a):
    #     a=a.reset_index()
    #     at=list(a.Ticker.astype('str'))
    #     at = ['0' * (6 - len(x)) + x for x in at]
    #     at=[x+'.SZ' if x[0]!='6' else x+'.SH' for x in at]
    #     a.Ticker=at
    #     a = a.set_index(['dt', 'minute'])
    #     a_dates=a.index.get_level_values(level=0).drop_duplicates()
    #     m_start=1430
    #     m_end=1500
    #     res=pd.DataFrame()
    #     amt_ratio_arr=[]
    #     for date in a_dates:
    #         day_tradings=a.loc[date]
    #         sample=day_tradings.loc[m_start:m_end,:]
    #         amt_ratio=sample.amt.sum()/day_tradings.amt.sum()
    #         amt_ratio_arr.append(amt_ratio)
    #     res['amt_'+str(m_start)+'_'+str(m_end)]=amt_ratio_arr
    #     res['Ticker']=at[0]
    #     res['dt']=a_dates
    #     return res
     
    # f=calc_wrapper_date(test_func,file_list)
    # f=f.set_index(['dt','Ticker'])
    # f=f.sort_index(level=0).dropna()
    # nl = neutralization.StyleFactorNeutralizer(start_date, end_date)
    # nl.load_basic_data(columns=['Industry', 'Size'])
    # IO.pd_hdf5_writer(f,hdf5='J:\\jlhHFT\\raw_factors\\tensor_1430_1500.h5',dataset=f.columns[0])
    # f_nl=nl.neutralize(f)
    # IO.pd_hdf5_writer(f_nl, hdf5='J:\\jlhHFT\\raw_factors\\tensor_1430_1500_nl.h5', dataset=f.columns[0])
    #aaa_dt=aaa.index.get_level_values(level=0).drop_duplicates()
    






