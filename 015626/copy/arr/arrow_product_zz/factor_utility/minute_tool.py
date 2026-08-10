# -*- coding: utf-8 -*-
"""
minute tool
"""

import matplotlib.pyplot as plt  
import numpy as np
import pandas as pd
import statsmodels.api as sm
import datetime as dt
import os
import time
import scipy.io as sio  


from line_profiler import LineProfiler
import numba
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

import sys
sys.path.insert(0, '..')
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from factor_utility.factor_tool import *


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

def ticker_match_reverse(ticker_str): # jit slow
    ticker_num = int(ticker_str[:-3])
    return ticker_num


def dt_parser(date):
    date_obj = dt.datetime.strptime(str(int(date)),'%Y%m%d')
    return date_obj


def dt_ticker_reformat(dat,dtype='df',reverse=False):
    if dtype=='mi' or dat.index.names == ['dt','Ticker']:
        dat = dat.reset_index()
        if reverse:
            dat['Ticker'] = dat['Ticker'].apply(lambda x: int(x[:-3]))
            dat['dt'] = dat['dt'].apply(lambda x:int(dt.datetime.strftime(x,'%Y%m%d')))
        else:
            dat['Ticker'] = dat['Ticker'].apply(ticker_match)
            dat['dt'] = dat['dt'].apply(dt_parser)
        dat = dat.set_index(['dt','Ticker'])    
    elif dtype=='df':
        if reverse:
            dat.columns = [int(i[:-3]) for i in dat.columns]
            dat.index = [int(dt.datetime.strftime(i,'%Y%m%d')) for i in dat.index]        
        else:
            dat.columns = [ticker_match(i) for i in dat.columns]
            dat.index = [dt_parser(i) for i in dat.index]
    return dat

def get_minute_list():
    minute_list_raw = [int('%d0%d'%(h,m)) if m<10 else int('%d%d'%(h,m)) for h in range(9,16) for m in range(0,60)]
    minute_list = [i for i in minute_list_raw if (i>929 and i<1130) or (i>1259 and i<1501) or (i==925)]
    return minute_list


@numba.jit
def minute_reformat_jit(dt_time):
    dt_hour = int(dt_time/3600)
    dt_minute = int((dt_time - dt_hour*3600)/60)
    time_use = dt_hour*100+dt_minute
    return time_use 

def miblock2df(dist_contain,normalize=True):
    if isinstance(dist_contain,pd.DataFrame):
        col_name = dist_contain.columns.tolist()
        print ('unstack for %s'%(col_name))
        fac_dict = {}
        for col in col_name:
            print (col)
            fac_dict[col] = dt_ticker_reformat(dist_contain[col].unstack())
            if normalize:
                fac_dict[col] = NormWinsor(fac_dict[col])
    elif isinstance(dist_contain,pd.Series):
        fac_dict = dt_ticker_reformat(dist_contain.unstack())
        if normalize:
            fac_dict = NormWinsor(fac_dict)
    return fac_dict


def miblock2dict(data_mi,normalize=True):
    col_name = data_mi.columns.tolist()
    block_list = data_mi.index.get_level_values(level=2).unique().tolist()
    block_list.sort()
    #type_list = [pd.Timestamp, str]
    #[type(i) for i in data_mi.head(1).index[0]]
    print (col_name)
    fac_dict = {k:{} for k in col_name}
    for col in col_name:
        print (col)
        _data = data_mi[col_name]
        for i in block_list:
            _slice = dt_ticker_reformat(_data.xs(i,level=2).unstack()[col])
            fac_dict[col][i] = NormWinsor(_slice) if normalize else _slice
    return fac_dict


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
    if isinstance(minute_num,pd.DataFrame) or isinstance(minute_num,pd.Series):
        minute_mat = minute_num.values
    else:
        minute_mat = minute_num
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

def get_minute_seg_dt(dat_raw,minute_duration):
    dt_list = dat_raw.index.tolist()
    hour_minute_list = np.array([int(dt.datetime.strftime(i,'%-H%M')) for i in dt_list])
    minute_seg = get_minute_seg(hour_minute_list,minute_duration)
    #minute_seg = [np.int(i) for i in minute_seg]
    minute_seg_pd = pd.DataFrame(minute_seg,index=dt_list,columns=['minute_seg'])
    return minute_seg_pd
    
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

def calc_stk_pm(dat,seg_num=4):
    dat['block'] = get_minute_block(dat['minute'],seg_num)
    block_last = dat[['close','block']].groupby(['dt','Ticker','block']).last()
    block_first = dat[['close','block']].groupby(['dt','Ticker','block']).first()
    pm_block = block_last/block_first-1
    return pm_block

def calc_minute_ret(dat):
    close2close = (dat['close']/dat['close'].shift(1)-1).values
    open2close = (dat['close']/dat['open']-1).values
    #mask_open_bid_1st_minute = (dat['minute']<=34200).values  # 33900 / 34200
    mask_open_bid_1st_minute = (dat['minute']==925).values  # 33900 / 34200
    close2close[mask_open_bid_1st_minute] = open2close[mask_open_bid_1st_minute]
    return close2close

def calc_minute_ret_log(dat):
    close2close = (np.log(dat['close']/dat['close'].shift(1))).values
    open2close = (np.log(dat['close']/dat['open'])).values
    #mask_open_bid_1st_minute = (dat['minute']<=34200).values  # 33900 / 34200
    mask_open_bid_1st_minute = (dat['minute']==925).values  # 33900 / 34200
    close2close[mask_open_bid_1st_minute] = open2close[mask_open_bid_1st_minute]
    return close2close

def calc_minute_ret_block(dat,minute_duration=30):
    dat['block'] = get_minute_seg(dat['minute'],minute_duration)
    dat['ret'] = calc_minute_ret(dat)
    dat_grp_block = dat.groupby(['dt','Ticker','block'])
    dat_ret = dat_grp_block[['ret']].sum()
    return dat_ret


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

"""
%timeit dat['ret1'] = calc_minute_ret(dat)
%timeit dat['ret2'] = calc_minute_ret2(dat)
dat[(dat['ret1'] - dat['ret2']).abs()>0]
"""
def calc_minute_ret2(dat):
    """ 
        minute return at t 
        9:25        - open bid: open(t)/close(t) - 1 
        9:30-14:59  - close(t-1)/close(t) - 1
        15:00       - close bid: open(t)/close(t) - 1 
    """
    dat['c2c'] = dat['close']/dat['close'].shift(1)-1
    dat['o2c'] = dat['close']/dat['open']-1
    dat['msk'] = dat['minute']==925
    dat['ret'] = dat['c2c']
    dat['ret'][dat['msk']] = dat['o2c']
    return dat['ret'].values

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



def mat2pickle(mat_file,pickle_file,reformat_minute=True):
    dat_mat = read_minute_mat_ultra(mat_file)
    if reformat_minute:
        dat_mat['minute'] = dat_mat['minute'].apply(raw2minute)        
    dat_mat.to_pickle(pickle_file,compression='gzip')
    return 

def migrate_mat2pickle(source_path,destination_path):
    # reading data
    print ('-'*20,'start','-'*20)
    
    if not os.path.exists(destination_path):
        print ('crate file: %s',destination_path)
        os.makedirs(destination_path)
    mat_list = [i for i in os.listdir(source_path)]
    file_list = [source_path+i for i in mat_list]
    file_list.sort()
    file_len = len(file_list)
    fail_list=[]
    index = True if source_path.find('Index')>1 else False
    for i in range(file_len):
        try:
            mat_file = file_list[i]
            print ('%d/%d'%(i+1,file_len),(mat_file))
            if index:
                pickle_file = destination_path+mat_file[-22:-4] + '.pkl'    
            else:
                pickle_file = destination_path+mat_file[-31:-4] + '.pkl'    
            mat2pickle(mat_file,pickle_file)
        except:
            print ('failed')
            fail_list.append(mat_file)
    print ('-'*20,'done','-'*20)
    return fail_list


def check_minute_data(dat):
    dat_count = dat.groupby(['dt','Ticker']).count()[['close']]
    return dat_count


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


def calc_slice_date_helper(file,calc_func,sdate=None,edate=None):
    dat = pd.read_pickle(file,compression='gzip')
    if sdate is not None:
        dat = slice_minute_data(dat,sdate,edate)            
    stats = calc_func(dat)
    return stats

def calc_minute_parallel_wrapper(calc_func,file_list=None,sdate=None,edate=None,max_process=None):
    # compute intensive
    if file_list is None:
        file_dict = get_minute_file()
        file_list = file_dict['stock']    
    read_calc_func = partial(calc_slice_date_helper,calc_func=calc_func,sdate=sdate,edate=edate)
    #calc_tail_ret_read(file_list[0])
    res_dict = multiprocess_wrapper(func=read_calc_func,iter_list=file_list,collect_output=True,max_process=max_process)
    res = pd.concat(list(res_dict.values()),axis=0)
    return res


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

