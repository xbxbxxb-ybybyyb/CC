# -*- coding: utf-8 -*-
"""
minute tool
"""


import matplotlib.pyplot as plt  
import numpy as np
import pandas as pd
import statsmodels.api as sm
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import datetime as dt
from multifactor.backtest.FactorTool import *
from multifactor.backtest import FactorTest
import os
import time
import scipy.io as sio  


from line_profiler import LineProfiler
import numba
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures


"""
from line_profiler import LineProfiler
lp = LineProfiler()
lp_wrapper = lp(read_minute_mat_quick)
lp_wrapper(file_path)
lp.print_stats()
"""

def str2minute(time_string):
    dt_year,dt_month,dt_date = int(time_string[:4]),int(time_string[4:6]),int(time_string[6:8])
    dt_time = int(time_string[8:])
    dt_hour = int(dt_time/3600)
    dt_minute = int((dt_time - dt_hour*3600)/60)
    time_obj = dt.datetime(dt_year,dt_month,dt_date,dt_hour,dt_minute)
    return time_obj


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



@numba.jit
def minute_reformat_jit(dt_time):
    dt_hour = int(dt_time/3600)
    dt_minute = int((dt_time - dt_hour*3600)/60)
    time_use = dt_hour*100+dt_minute
    return time_use 

def miblock2df(dist_contain,normalize=True):
    col_name = dist_contain.columns.tolist()
    fac_dict = {}
    for col in col_name:
        print (col)
        fac_dict[col] = dt_ticker_reformat(dist_contain[col].unstack())
        if normalize:
            fac_dict[col] = NormWinsor(fac_dict[col])
    return fac_dict




def read_minute_mat(file_path):
    id_pos = file_path.rfind('\\')
    fname = file_path[id_pos+1:]
    header_list = ['date','time','open','high','low','close','volume','amt']
    data_config = {'type_date_time':    ['date','time'],
                   'type_float':        ['open','high','low','close','volume','amt']}
    dat1 = sio.loadmat(file_path)  # 做多
    dat = pd.DataFrame(dat1[fname[:-4]],columns=header_list)
    dat['Ticker'] = int(fname[-10:-4])
    dat['Ticker'] = dat['Ticker'].astype('int32')
    dat[data_config['type_float']] =  dat[data_config['type_float']].astype('float32')
    dat[data_config['type_date_time']] =  dat[data_config['type_date_time']].astype('int32')
    dat[data_config['type_date_time']] =  dat[data_config['type_date_time']].astype('str')
    dat['date_time_str'] = dat['date']+dat['time']
    dat['dt'] = dat['date_time_str'].apply(str2minute)
    dat = dat.drop(['date','time','date_time_str'],axis=1)
    dat = dat.set_index(['dt','Ticker'])
    return dat

def read_minute_mat_quick(file_path):
    id_pos = file_path.rfind('\\')
    fname = file_path[id_pos+1:]
    header_list = ['dt','minute','open','high','low','close','volume','amt']
    dat1 = sio.loadmat(file_path)  
    dat = pd.DataFrame(dat1[fname[:-4]],columns=header_list)
    dat['Ticker'] = int(fname[-10:-4])
    dat['dt'] = dat['dt'].astype('int32')
    dat['minute'] = dat['minute'].apply(minute_reformat_jit)    
    dat = dat.set_index(['dt','Ticker'])
    return dat

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

def minute2raw(minute_read):
    dt_hour=int(minute_read/100)
    dt_min = int(str(minute_read)[-2:])
    minute_raw = dt_hour*3600+dt_min*60
    return minute_raw

def raw2minute(minute_raw):
    minute_raw = int(minute_raw)
    dt_hour = int(minute_raw/3600)
    dt_min = int((minute_raw - dt_hour*3600)/60)
    minute_read = dt_hour*100+dt_min
    return minute_read


"""possible retire"""
def get_minute_block(minute_num,seg_num=4):
    # 925:bidding / 930: 930-931  / ignore 1500
    minute_mat = minute_num.values
    minute_block = np.array([np.nan]*len(minute_num))
    minute_type = 'raw' if minute_mat[0:2].mean()>2000 else 'process'
    # note - 1459:53940 / 15:00 - 54000 --- wind data is labeled at the start of minute 
    # to include close bell bid time --- last block
    if minute_type=='raw':
        if seg_num==4:
            #seg = [[34200,37740],[37800,41340],[46800,50340],[50400,53940]]
            seg = [[34200,37740],[37800,41340],[46800,50340],[50400,53940]]
        if seg_num==2:
            seg = [[34200,41340],[46800,53940]]     
        if seg_num==8:
            seg = [[34200,35940],[36000,37740],[37800,39540],[39600,41340],[46800,48540],[48600,50340],[50400,52140],[52200,53940]]
    elif minute_type=='process':
        if seg_num==4:
            seg = [[930,1029],[1030,1129],[1300,1359],[1400,1459]]
        if seg_num==2:
            seg = [[930,1129],[13001459]]
        if seg_num==8:
            seg = [[930,959],[1000,1029],[1030,1059],[1100,1129],[1300,1329],[1330,1359],[1400,1429],[1430,1459]]
    for i in range(seg_num):
        minute_block[(minute_mat>=seg[i][0]) & (minute_mat<=seg[i][1])] = i+1
    return minute_block



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



def minute_block_intraday(minute_num):
    # 925:bidding / 930: 930-931  / ignore 1500
    minute_mat = minute_num.values
    minute_block = np.array([np.nan]*len(minute_num))
    seg = [925,1459]
    #minute_block[(minute_mat<=seg[0])] = 1
    #minute_block[(minute_mat>=seg[1])] = 2
    minute_block[minute_mat==seg[0]] = 1
    minute_block[minute_mat==seg[1]] = 2
    return minute_block



#dat['block_intrday'] = minute_block_intraday(dat['minute'])
#pm_block_intraday = dat[dat['block_intrday']==1]['close'] / dat[dat['block_intrday']==2]['close'].shift(1)

def calc_stk_pm(dat):
    dat['block'] = get_minute_block(dat['minute'])
    block_last = dat[['close','block']].groupby(['dt','Ticker','block']).last()
    block_first = dat[['close','block']].groupby(['dt','Ticker','block']).first()
    pm_block = block_last/block_first-1
    return pm_block



def calc_pm(file_list):
    pm_contain = pd.DataFrame()    
    stock_num = len(file_list) if type(file_list)==list else 1
    for i in range(stock_num):
        try:
            if stock_num>1:
                file_path = file_list[i] 
                print (i,'/',stock_num,'---',file_path[-10:-4])    
            else:
                file_path = file_list
            dat = read_minute_mat_ultra(file_path)
            pm_block = calc_stk_pm(dat)
            pm_contain = pm_contain.append(pm_block)
        except:
            print ('fail!!!!!!!')
    return pm_contain


def block2mi(dist_contain):
    col_name = dist_contain.columns.tolist()
    fac_dict = {}
    for col in col_name:
        print (col)
        fac_dict[col] = dt_ticker_reformat(dist_contain[col].unstack(),dtype='mi')
        fac_dict[col].columns = [col+str(int(i)) for i in fac_dict[col].columns]
    return fac_dict

def calc_minute_ret(dat):
    close2close = (dat['close']/dat['close'].shift(1)-1).values
    open2close = (dat['close']/dat['open']-1).values
    mask_open_bid_1st_minute = (dat['minute']<=34200).values  # 33900 / 34200
    close2close[mask_open_bid_1st_minute] = open2close[mask_open_bid_1st_minute]
    return close2close

def calc_stk_basic_block(dat,minute_duration=30):
    dat['block'] = get_minute_seg(dat['minute'],minute_duration)
    #dat['ret_minute1'] = dat['close']/dat['open'] - 1
    dat['ret_minute'] = calc_minute_ret(dat)
    dat['volume*close'] = dat['volume']*dat['close']
    dat['sign(ret)*amt'] = np.sign(dat['ret_minute'])*dat['amt']
    dat_grp_block = dat.groupby(['dt','Ticker','block'])
    dat_ret = dat_grp_block['ret_minute'].sum()
    dat_ret = pd.DataFrame(dat_grp_block['close'].last()/dat_grp_block['open'].first()-1,columns=['ret'])
    dat_ret['volume'] = dat_grp_block['volume'].sum()
    dat_ret['mstd'] = dat_grp_block['ret_minute'].std()
    dat_ret['amt'] = dat_grp_block['amt'].sum()
    dat_ret['mf'] = dat_grp_block['sign(ret)*amt'].sum()
    #dat_ret['close'] = dat_grp_block['close'].last()
    dat_ret['vwap'] = dat_grp_block['volume*close'].sum()/dat_ret['volume']
    dat_ret['sharpe'] = dat_ret['ret']/dat_ret['mstd']
    return dat_ret


def slice_minute_range(dat,minute_bound=[34200,53760]):
    dat_take = dat[(dat['minute']<=minute_bound[0]) | (dat['minute']>=minute_bound[1])]
    return dat_take 




################ For mutli thread - faster read and compute ########################################
def calc_wrapper(read_func,compute_func,file_path):
    try:
        dat = read_func(file_path)
    except:
        print ('read fail')
    try:
        dat_result = compute_func(dat)
    except:
        print ('calc fail')
    return dat_result


def func_parallel(func,input_list,max_workers=10):
    # estimation time: 8 min for 3500 stocks
    tic = time.time()
    total_job = len(input_list)
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func, file_path): file_path for file_path in input_list}
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


################ For mutli thread - faster read and compute ########################################

def slice_minute_data(dat,start_date,end_date):
    dat['date'] = dat.index.get_level_values(0)
    dat['take'] = (dat['date']>=start_date) & (dat['date']<= end_date)
    dat_slice = dat[dat['take']==True].iloc[:,:-2]
    return dat_slice


def calc_stats(file_list,start_date=None,end_date=None):
    pm_list = []
    stock_num = len(file_list) if type(file_list)==list else 1
    for i in range(stock_num):
        try:
            if stock_num>1:
                file_path = file_list[i] 
                print (i,'/',stock_num,'---',file_path[-10:-4])    
            else:
                file_path = file_list
            dat = read_minute_mat_ultra(file_path)
            if start_date is not None:
                dat = slice_minute_data(dat,start_date,end_date)
            stat_raw = calc_stk_stats(dat)
            stats = parse_stats_output(stat_raw)
            pm_list.append(stats)
        except:
            print ('fail!!!!!!!')
    pm_contain = pd.concat(pm_list,axis=0)
    return pm_contain


def calc_stk_dist_roll(dat,roll_win=20,minute_duration=5):
    if minute_duration==5:
        dat['block'] = get_minute_seg(dat['minute'],minute_duration)
        dat_grp = dat.groupby(['dt','Ticker','block'])
        dat_ret = dat_grp['close'].last()/dat_grp['open'].first()-1
    elif minute_duration ==1:
        dat['ret'] = dat['close']/dat['open'] - 1
        dat_ret = dat[['ret']]
    block_num = int(242/minute_duration)
    min_pct = 0.5
    min_num = block_num*roll_win*min_pct
    date_list = list(set(dat.index.get_level_values(0)))
    day_num = len(date_list)
    ticker = dat.iloc[0].name[1]
    new_index = list(zip(*(np.array([date_list,[ticker]*day_num]))))
    index_use = pd.MultiIndex.from_tuples(new_index, names=['dt', 'Ticker'])
    rebal_num = int(day_num - roll_win + 1)
    std_mat = np.zeros([day_num,3])
    std_mat[:] = np.nan
    count_list = list(dat_ret.groupby('dt').cumcount().values)
    index_list = [i for i, j in enumerate(count_list) if j == 0]
    index_list.append(len(dat_ret))
    dat_ret_mat = dat_ret.values
    for idx in range(rebal_num):
        #date_use = date_list[idx:idx+roll_win+1]
        #dat_use_date = dat_ret.loc[date_use].values
        #dat_use_date1 = dat_ret[(dat_ret['date']<=date_use[-1]) & (dat_ret['date']>=date_use[0])].values
        #dat_use_date = dat_ret_mat[index_list[idx]:index_list[idx+roll_win]]
        #ret = dat_use_date[:,0]
        ret = dat_ret_mat[index_list[idx]:index_list[idx+roll_win]]
        ret_mask = np.isfinite(ret)
        ret_use = ret[ret_mask] 
        ret_up = ret_use[ret_use>0]
        ret_up_mask = np.isfinite(ret_up)
        if np.count_nonzero(ret_mask)>=min_num:
            std_mat[idx+roll_win-1,0] = np.std(ret_use)
            std_mat[idx+roll_win-1,1] = np.std(ret_up[ret_up_mask])
            std_mat[idx+roll_win-1:,2] = std_mat[idx+roll_win-1:,1]/std_mat[idx+roll_win-1:,0]
    stats = pd.DataFrame(std_mat,columns=['ret_std','ret_up_std','ret_up_std_ratio'],index=index_use)
    return stats


def func_parallel_date(func,input_list,sdate,edate,max_workers=10):
    # estimation time: 8 min for 3500 stocks
    tic = time.time()
    total_job = len(input_list)
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func,file_path,sdate,edate): file_path for file_path in input_list}
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

def check_minute_data(dat):
    dat_count = dat.groupby(['dt','Ticker']).count()[['close']]
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



def calc_wrapper_date_params(func,file_list,*args,sdate=None,edate=None,**kwargs):
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
            stats = func(dat,*args,**kwargs)
            pm_list.append(stats)
        except:
            print ('fail!!!!!!!')
    pm_contain = pd.concat(pm_list,axis=0)
    return pm_contain

def func_parallel_wrap_date_params(func,input_list,*args, sdate=None,edate=None,max_workers=10, **kwargs):
    # estimation time: 8 min for 3500 stocks
    tic = time.time()
    total_job = len(input_list)
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(calc_wrapper_date_params,func,file_path,*args,sdate=sdate,edate=edate,**kwargs): file_path for file_path in input_list}
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


################ Block data ########################################

def get_minute_block1(minute_num,seg):
    # 925:bidding / 930: 930-931  / ignore 1500
    minute_mat = minute_num.values
    minute_block = np.array([np.nan]*len(minute_num))
    seg_num = len(seg)        
    for i in range(seg_num):
        minute_block[(minute_mat>=seg[i][0]) & (minute_mat<=seg[i][1])] = i+1
    return minute_block

def get_open_close_data(dat,seg):
    dat['block'] = get_minute_block1(dat['minute'],seg)
    dat_take = dat.dropna(subset=['block'], how='all')[['minute','open','close','volume','block']]
    return dat_take

def get_open_close_data(file_path):
    # eta: 335s 
    try:
        dat = read_minute_mat_ultra(file_path)
    except:
        print ('read fail')
    try:
        seg = [[34200, 34320], [41220, 41340], [46800, 46920], [53820, 53940]]
        dat['block'] = get_minute_block1(dat['minute'],seg)
        #dat_take = dat.dropna(subset=['block'], how='all')[['minute','open','close','volume','block']]
        dat_take  = dat[np.isfinite(dat['block'])][['minute','open','close','volume','block']]
    except:
        print ('take fail')
    return dat_take





"""
from multiprocessing import Pool, Process

if __name__ == '__main__':
    process_num = 4
    with Pool(processes=process_num) as pool:
        handlers = []
        for bn in [2, 4]:
            handler = pool.apply_async(update_minute_calc, kwds={'block_num': bn, 'sdate': 20130101, 'edate': 20180508, 'operation': 'create'})
            handlers.append(handler)
        [job.get() for job in handlers]
"""

