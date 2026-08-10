# -*- coding: utf-8 -*-
"""
update_concensus_htsc

"""



# -*- coding: utf-8 -*-
"""
update wind_db from htsc matlab

"""


import datetime as dt
import pandas as pd
import scipy.io as sio  
import os
import numpy as np
import json
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import os
import subprocess
from functools import partial

import time
import scipy.io as sio  


# from line_profiler import LineProfiler
import numba
# from concurrent.futures import ThreadPoolExecutor
# import concurrent.futures



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

    

def matlab_executer(input_tuple,mat_fig):
    
    """
    mat_fig = {'matlab_path': '\"D:\\012315\\MATLAB Production Server\\R2015a\\bin\\matlab.exe"',
               'matlab_code_path':'D:\\012315\\Code\\data_updater',
               'matlab_function':'updater_universe_csv'}
    
    mat_fig = {'matlab_path': '\"D:\\012315\\MATLAB Production Server\\R2015a\\bin\\matlab.exe"',
               'matlab_code_path':'D:\\012315\\Code\\AlphaFactor\\AlphaSystem\\PythonVersion\\Data\\',
               'matlab_function':'update_wind_htsc'}
    input_tuple = [20180101,20180328,'WIND_AShareFinancialIndicator']

    """    
    print ('Calling Matlab to download data...')
    print (input_tuple)

    matlab_path = mat_fig['matlab_path']#'\"D:\\012315\\MATLAB Production Server\\R2015a\\bin\\matlab.exe"'
    matlab_code_path = mat_fig['matlab_code_path']  # 'D:\\012315\\Code\\data_updater'
    matlab_function = mat_fig['matlab_function']  # 'updater_universe_csv'
    
    input_str = ''
    for ele in input_tuple:
        if type(ele)==str:
            cat = "'"+ele+"'"
        else:
            cat = str(ele)
        input_str = input_str+cat if input_str is '' else input_str+','+cat 
        
    run_matlab = matlab_path + ' -nodesktop -nosplash -r -wait \"'+matlab_function+'('+input_str+')\"'+';quit;'
    subprocess.call(run_matlab,cwd=matlab_code_path)
    print ('Download complete')
    return 


def get_sub(a,lvl=1,replace=np.nan):
    try:
        if lvl==1:
            b = a[0]
        if lvl==2:
            b = a[0][0]
    except: 
        b = replace
    return b
        


def ticker_match(ticker_num): # jit slow
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker



def mat_reformat(dat,dat_fig):
    dat_name = list(dat.keys())[-1]
    header_list = [i[0] for i in dat[dat_name][0,:]]
    dat = pd.DataFrame(dat[dat_name][1:,:],columns=header_list)
    if 'drop' in dat_fig.keys():
        dat = dat.drop(dat_fig['drop'],axis=1)
        for drop_col in dat_fig['drop']:
            header_list.remove(drop_col)
    #format_list = [type(i[0][0]) for i in dat.iloc[0,:]]
    format_list = []
    for i in dat.iloc[0,:]:
        try:
            format_list.append(type(i[0][0]))        
        except:
            format_list.append(str)
    str_list = [i==str for i in format_list]
    num_list = [i!=str for i in format_list]
    dat.iloc[:,num_list] = dat.iloc[:,num_list].applymap(lambda x:x[0][0]) 
    dat.iloc[:,str_list] = dat.iloc[:,str_list].applymap(lambda x:x[0] if len(x)>0 else '')
    dat[np.array(header_list)[num_list]] = dat[np.array(header_list)[num_list]].astype('float64')    
    #dat = dat.sort_values([dat_fig['dt']])
    dat[dat_fig['dt']] = dat[dat_fig['dt']].apply(lambda x: dt.datetime.strptime(str(int(x)),'%Y%m%d'))
    if 'ticker_match' in dat_fig.keys():
        dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].apply(ticker_match)
    else:
        dat[dat_fig['Ticker']] = dat[dat_fig['Ticker']].astype('str')
    dat = dat.sort_values([dat_fig['dt'],dat_fig['Ticker']])
    dat = dat.set_index([dat_fig['dt'],dat_fig['Ticker']])
    dat.index.names = ['dt','Ticker']
    return dat


"""
fname = 'S:\\Quant\\backtest\\local_data\\wind_htsc\\WIND_AShareProfitExpress\\20171231.mat'
dat_raw = sio.loadmat(fname) 
dat_fig = {'dt':'REPORT_PERIOD','Ticker':'S_INFO_WINDCODE'}
dat = mat_reformat(dat_raw,dat_fig)

fname = 'S:\\Quant\\backtest\\local_data\\wind_htsc\\WIND_AShareFinancialIndicator\\20171231.mat'
dat_raw = sio.loadmat(fname) 
dat_fig = {'dt':'REPORT_PERIOD','Ticker':'S_INFO_WINDCODE'}
dat = mat_reformat(dat_raw,dat_fig)

fname = 'S:\\Quant\\backtest\\local_data\\wind_htsc\\WIND_AShareProfitNotice\\20171231.mat'
dat_raw = sio.loadmat(fname) 
dat_fig = {'dt':'S_PROFITNOTICE_PERIOD','Ticker':'S_INFO_WINDCODE'}
dat = mat_reformat(dat_raw,dat_fig)

fname = 'S:\\Quant\\backtest\\local_data\\wind_htsc\\WIND_AShareTTMHis\\20171231.mat'
dat_raw = sio.loadmat(fname) 
dat_fig = {'dt':'REPORT_PERIOD','Ticker':'S_INFO_WINDCODE'}
dat = mat_reformat(dat_raw,dat_fig)
"""


"""dump data"""



"""fundamental data: back fill quarterly to daily data"""
def int2date(date_int,date_format='%Y%m%d'):
    if np.isfinite(date_int):
        date_time = dt.datetime.strptime(str(int(date_int)),'%Y%m%d')
    else:
        date_time = date_int
    return date_time

def dat_operation(dat,op_fig):
    dat = dat.drop(op_fig['drop'],axis=1)
    def rep_dict(x,rename_dict): return rename_dict[x] if x in rename_dict.keys() else x 
    col_name = [rep_dict(i.replace('S_DQ_','').lower(),op_fig['rename_dict']) for i in dat.columns]
    dat.columns= col_name
    return dat    


def mat2h5_generic(func_reformat,mat_list,h5_path,table_name,operation,min_size=0,csv_path=None):
    
    fail_list = []
    mat_list.sort()
    
    if operation=='create':
        print ('Create new h5: '+h5_path)
        if os.path.exists(h5_path):
            print ('Remove existing h5:',h5_path)
            os.remove(h5_path) 
    elif operation == 'append':
        print ('Append to: '+ h5_path)
    with pd.HDFStore(h5_path) as h5_store:
        print ('check date list takes some time')
        if table_name in list(h5_store.root._v_groups.keys()):
            # dataset is already created
            dt_lst = list(set(h5_store.select_column(table_name, 'dt')))
        else:
            dt_lst = []
        for fname in mat_list:
            print (fname)
            try:
                print ('read')
                dat = sio.loadmat(fname)  
                dat_format = func_reformat(dat)
                if csv_path is not None:
                    print ('to csv')
                    dat_format.to_csv(csv_path+str(fname[-12:-4])+'.csv')
                try:
                    if len(dat)<min_size:
                        print ('mat data too little!')
                        fail_list.append(fname+'@amount_fail')
                    else:
                        if operation == 'append':      
                            curr_date = list(set(dat_format.index.get_level_values('dt')))[0]
                            print (curr_date)
                            if curr_date in dt_lst:
                                print ('Remove: '+str(curr_date))
                                dummy_id = h5_store.remove(table_name,'dt=curr_date')
                                print ('Append: '+str(curr_date))
                        print ('insert')
                        h5_store.append(table_name,dat_format,data_columns=True)
                        print ('done')
                except:
                    print (str(fname)+' save to h5 failed')  
                    fail_list.append(fname+'@h5_fail')
            except: 
                print (str(fname)+' read failed!')
                fail_list.append(fname+'@read_fail')
    print ('data loading complete!')     
    return fail_list


#table_list = ['stock_order3','stock_order2','stock_report_adjustment2','stock_report_adjustment','stock_concern_level']
#output = io_parallel_date(update_consensus_htsc,table_list[:2],sdate,edate,operation)


def io_parallel_date(func,table_list,sdate,edate,operation,max_workers=5):
    # estimation time: 8 min for 3500 stocks
    tic = time.time()
    total_job = len(table_list)
    print ('-'*20,' Start ','-'*20)
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file_list = {executor.submit(func,table_name,sdate,edate,operation): table_name for table_name in table_list}
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
                print('%d/%d - %r has %d rows' % (table_list.index(file_path)+1,total_job,file_path, len(data)))
        print ('concating results')
        data_collector = pd.concat(list_collector,axis=0)
    toc = time.time()
    print (toc-tic)
    print ('-'*20,' End ','-'*20)
    return data_collector


def mat2csv(func_reformat,mat_list,csv_path_table):
    fail_list = []
    mat_list = [mat_list] if type(mat_list) is str else mat_list
    print ('saving mat to csv')
    for fname in mat_list:
        date = fname[-12:-4]
        print (date)
        try:
            dat = sio.loadmat(fname)  
            dat_format = func_reformat(dat)        
            dat_format.to_csv(csv_path_table+str(date)+'.csv')
        except:
            print ('error')
            fail_list.append(date)
    return fail_list


def update_consensus_table(table_name,sdate=None,edate=None,operation='append',pull_data=True,mat2csv=True):
    root_data_path = 'D:\\Quant\\backtest\\local_data\\'
    root_h5_path = 'D:\\Quant\\data\\'
    
    csv_path = root_data_path+'gogoal_htsc\\csv\\'
    csv_path_table = csv_path+table_name+'\\'
    os.mkdir(csv_path_table) if not os.path.exists(csv_path_table) else None
    print ('update for:'+str(sdate)+'-'+str(edate))
    sdate,edate,cdate_list = check_update_date(sdate,edate,use_len=0)
    
    if pull_data:
        print ('download data from sql')
        input_tuple = [sdate,edate,table_name]
        mat_fig = {'matlab_path': '\"D:\\013160\matlab\\MATLAB_Production_Server\\R2015a\\bin\\matlab.exe"',
                   'matlab_code_path':'D:\\013160\\data_update\\concensus\\',
                   'matlab_function':'update_concensus_htsc'}        
        matlab_executer(input_tuple,mat_fig)
    else:
        print ('skip download')
        
    source_path = root_data_path + '\\gogoal_htsc\\'+ table_name + '\\'
   
    if table_name =='con_forecast_stk':
        h5_path = root_h5_path+'fcd\\CHINA_STOCK\\DAILY\\HTSC\\FCD_CHINA_STOCK_DAILY_HTSC.h5'
    else:
        h5_path = root_h5_path+'fcd\\CHINA_STOCK\\DAILY\\HTSC\\'+ table_name + '.h5'
    
    mat_list = [source_path+i for i in os.listdir(source_path)]
    mat_list.sort()
    mat_date_list = [int(i[-12:-4]) for i in mat_list]
    
    print('check exist list')
    mat_date_list_take = [i for i in mat_date_list if i>=sdate and i<=edate]
    mat_list_take = [source_path+str(i)+'.mat' for i in mat_date_list_take]
    mat_list_take.sort()
    
    if len(mat_date_list_take) != len(cdate_list):
        print ('No mat file for:\n' + str(list(set(cdate_list) - set(mat_date_list_take))))
        raise Exception
    print ('dump mat file to h5')
    if table_name not in ['con_forecast_schedule','con_forecast_stk','stock_diversity',
                          'con_stock_deviation','stock_diversity','stock_emotion',
                          'stock_report_extremum','stock_report_number']:
        dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE','drop':['CONKEYTMS']}
    else:
        dat_fig = {'dt':'TDATE','Ticker':'STOCK_CODE','ticker_match':'STOCK_CODE'}    
    func_reformat = partial(mat_reformat,dat_fig=dat_fig)
    if mat2csv:
        fail_list = mat2h5_generic(func_reformat,mat_list_take,h5_path,table_name,operation,min_size=0,csv_path=csv_path_table)
    else:
        fail_list = mat2h5_generic(func_reformat,mat_list_take,h5_path,table_name,operation,min_size=0,csv_path=None)
    return fail_list



def update_consensus_data(sdate=None,edate=None,operation='append'):
    # operation = 'create'
    print ('-'*40,'update concensus data','-'*40)

    table_list = ['con_forecast_stk','con_forecast_schedule','stock_order3','stock_order2',
                  'stock_report_adjustment2','stock_report_adjustment','stock_concern_level',
                  'con_stock_deviation3','con_stock_deviation2','con_stock_deviation',
                  'stock_diversity','stock_emotion','stock_report_extremum','stock_report_number']

    print ('update for:'+str(sdate)+'-'+str(edate))
    sdate,edate,cdate_list = check_update_date(sdate,edate,use_len=0)    

    fail_dict = {}
    for table_name in table_list:
        print ('-'*40,table_name,'-'*40)
        fail_dict[table_name] = update_consensus_table(table_name,sdate,edate,operation,pull_data=True)
        print ('-'*40,'done','-'*40)

    mat_path = 'D:\\Quant\\backtest\\local_data\\gogoal_htsc\\'

    fail_dict_master ={}
 
    """record fail"""
    print (fail_dict_master)
    log_path = mat_path+'log\\'
    os.mkdir(log_path) if not os.path.exists(log_path) else None
    log_file = mat_path+'log\\'+str(cdate_list[-1])+'.json'
    with open(log_file, 'w') as f:
        json.dump(fail_dict_master, f)
    print ('-'*40,'all done','-'*40)
    return fail_dict
   
# update_consensus_data()     
"""
sdate,edate = 20090101,20180426
#fail_dict = update_consensus_data(sdate,edate,operation='append')
table_list = ['con_forecast_stk','con_forecast_schedule','stock_order3','stock_order2',
              'stock_report_adjustment2','stock_report_adjustment','stock_concern_level',
              'con_stock_deviation3','con_stock_deviation2','con_stock_deviation',
              'stock_diversity','stock_emotion','stock_report_extremum','stock_report_number']
#table_name = table_list[8]

#for table_name in ['con_stock_deviation','stock_diversity','stock_emotion']:
for table_name in ['stock_report_extremum','stock_report_number']:
    print (table_name)
    update_consensus_table(table_name,sdate,edate,operation='create',pull_data=True,mat2csv=True)

"""

















































































































