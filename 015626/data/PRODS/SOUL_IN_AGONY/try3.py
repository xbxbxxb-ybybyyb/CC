import bottleneck as bk
import pandas as pd
import numpy as np
import inspect,os,sys,time,pickle
import datetime as dt
import sys
import os
import datetime
import json
from joblib import Parallel, delayed
from xquant.xqutils.helper import link


full_date = '20240628'

version_list = ['im_v1unifac', 
                ]

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

################## model setting ###################
# manual update for each model update date


version_ticker_dict = {'if_v7_crn':'IF.CFE', 'if_v7c':'IF.CFE', 
                       'ic_v7unifac_crn': 'IC.CFE', 'ic_v7unifac': 'IC.CFE', 
                       'ic_v8unifac_crn': 'IC.CFE', 'ic_v75unifac': 'IC.CFE', 
                       'im_v1unifac_crn': 'IM.CFE', 'im_v1unifac': 'IM.CFE',
                       'ic_v7unifac_crn_trend': 'IC.CFE', 'if_v7_crn_trend':'IF.CFE', 'im_v1unifac_crn_trend': 'IM.CFE'}

model_date_dict = {
                   'if_v7c':'%s_if_if_v7c'%full_date,
                   'if_v7c2':'20230120_if_if_v7c2',
                   'if_v7_crn':'%s_if_if_v7_crn'%full_date, 
                   'if_v7_crn_trend':'%s_if_if_v7_crn_trend'%full_date,                  
                   
                
                   'ic_v7unifac':'%s_ic_ic_v7unifac'%full_date,
                   'ic_v7unifac_crn': '%s_ic_ic_v7unifac_crn'%full_date,
                   'ic_v7unifac_crn_trend': '%s_ic_ic_v7unifac_crn_trend'%full_date,
                   'ic_v75unifac':'%s_ic_ic_v7unifac_old'%full_date,
                   'ic_v8unifac_crn': '%s_ic_ic_v8unifac_crn'%full_date,
                   'im_v1unifac_crn': '%s_im_im_v1unifac_crn'%full_date, 
                   'im_v1unifac_crn_trend': '%s_im_im_v1unifac_crn_trend'%full_date, 
                   'im_v1unifac': '%s_im_im_v1unifac'%full_date, 
                }
'''
model_date_use_dict = {
                       'if_v7_crn':'%s'%(model_date_dict['if_v7_crn']),
                       'if_v7c':'%s'%(model_date_dict['if_v7_crn']),
                       'ic_v7unifac_crn':'%s'%(model_date_dict['ic_v7unifac_crn']),
                       'ic_v7unifac':'%s'%(model_date_dict['ic_v7unifac']),
                       'ic_v8unifac_crn':'%s'%(model_date_dict['ic_v8unifac_crn']),
                       'ic_v75unifac':'%s'%(model_date_dict['ic_v75unifac']),
                       'im_v1unifac_crn':'%s'%(model_date_dict['im_v1unifac_crn']),
                       'im_v1unifac':'%s'%(model_date_dict['im_v1unifac']),
                       }
                    
'''
min_pct = 0.96
use_update = True
dropna = True
return_itr = True
check_time = False
ma_day = 10

process_list = None
train_s = '2016'
slice_range_extra = [[931,1129],[1300,1456]]

################## path setting ###################
 
dat_root = '/data/group/800466/warehouse/prod'                   

# function used
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(code_base)
#pa = '/data/user/012315/alpha'
#sys.path.insert(0, pa)
sys.path.insert(0, os.path.dirname(code_base))
# change to your only IO root
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
from sklearn.preprocessing import StandardScaler
from keras.models import load_model
from multiprocessing import Pool
import multifactor.utility.dt as udt

sim = False
sim_if = False

if sim == True:
    trail = '_new'
else:
    trail = ''

if sim_if == True:
    trail_if = '_new'
else:
    trail_if = ''

_,eedate,date_list = check_update_date()



def gen_history_factor_values(date_str, factor_value_path, save_path, write_type = "w"):
    from_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    to_date = from_date + datetime.timedelta(1)
    to_date_str = datetime.datetime.strftime(to_date, "%Y-%m-%d")
    
    sp = date_str.split('-')
    file_name = ''
    for item in sp:
        file_name = file_name + item
    fw = open(os.path.join(save_path,file_name), write_type)

    dir_name = factor_value_path
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            full_name = os.path.join(root, f)
            factor_name = f[0:-3]
            if factor_name in ['minute_seg_1','minute_seg_2','minute_seg_3','minute_seg_4']:
                factor_file_name = factor_name + '.0'
            else:
                factor_file_name = factor_name
            data = pd.read_hdf(full_name)
            data = data.reset_index()
            col_set = set(data.columns)
            #print('begin to get ' + factor_name + ' history value')
            if (col_set.__contains__('index')):
                dest_data = data[data['index']>date_str]
                dest_data = dest_data[dest_data['index'] < to_date_str]
                dest_data[factor_name] = dest_data[factor_name].astype('float64')
                factor_value_list = list(dest_data[factor_name].values)
                #print(factor_name + ': ' + str(len(factor_value_list)))
                factor_dict = {}
                factor_dict['FactorName'] = factor_file_name
                factor_dict['Values'] = factor_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')
            elif col_set.__contains__("dt"):
                dest_data = data[data['dt']>date_str]
                dest_data = dest_data[dest_data['dt'] < to_date_str]
                dest_data[factor_name] = dest_data[factor_name].astype('float64')
                factor_value_list = list(dest_data[factor_name].values)
                #print(factor_name + ': ' + str(len(factor_value_list)))
                factor_dict = {}
                factor_dict['FactorName'] = factor_file_name
                factor_dict['Values'] = factor_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')
    fw.close()
    
def gen_history_signal_values(date_str, signal_value_path, save_path):
    from_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
    to_date = from_date + datetime.timedelta(1)
    to_date_str = datetime.datetime.strftime(to_date, "%Y-%m-%d")

    sp = date_str.split('-')
    file_name = ''
    for item in sp:
        file_name = file_name + item
    fw = open(os.path.join(save_path, file_name), "w")

    dir_name = signal_value_path
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            full_name = os.path.join(root, f)

            data = pd.read_pickle(full_name)
            col_set = set(data.columns)

            dest_data = data[data.index>date_str]
            dest_data = dest_data[dest_data.index < to_date_str]
            for col in list(dest_data.columns):
                dest_data[col] = dest_data[col].astype('float64')
                signal_value_list = list(dest_data[col].values)
                print(col + ': ' + str(len(signal_value_list)))
                factor_dict = {}
                factor_dict['SignalName'] = col
                factor_dict['Values'] = signal_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')
    fw.close()
    
def gen_history_signal_values_2(date_str1, signal_value_path, index_list, save_path):

    date_str = str(date_str1)
    sp = date_str.split('-')
    file_name = ''
    for item in sp:
        file_name = file_name + item
    fw = open(os.path.join(save_path, file_name), "w")

    dir_name = signal_value_path
    for root, dirs, files in os.walk(dir_name):
        for f in files:
            full_name = os.path.join(root, f)

            data = pd.read_pickle(full_name)
            col_set = set(data.columns)

            dest_data = data.loc[index_list]
            
            for col in list(dest_data.columns):
                dest_data[col] = dest_data[col].astype('float64')
                signal_value_list = list(dest_data[col].sort_values(ascending = True).values)
                print(col + ': ' + str(len(signal_value_list)))
                factor_dict = {}
                factor_dict['SignalName'] = col
                factor_dict['Values'] = signal_value_list
                s = json.dumps(factor_dict)
                fw.write(s + '\n')
    fw.close()
    
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'    
def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_ic_factors.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_if_factors.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_model.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_model_v7.success'
    path5 = flag_rootpath + str(date) + '/' + 'NORM2.success'
    
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path5)


for datee in date_list:
    
    date = str(datee)
    print(date)
    flag_path = flag_rootpath + str(date) + '/'
    if not os.path.exists(flag_path):
        os.makedirs(flag_path)
    flag_path_start = flag_path + str(date) + '_norm2_generation.start'
    with open(flag_path_start,'w') as file:
        pass 

    print('------wait data flag')
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')
    print('START')

    for version in version_list:
        print(version)
        cat = version_ticker_dict[version].lower().split('.')[0]
        
          
        model_date = str(model_date_dict[version])# + cat
        model_date2 = model_date# + '_' + version
        next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
        
        start_date = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
        days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

        model_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw/%s' % (str(model_date), str(date))
        save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/signalNorm2Value' % (next_tday + '_' + model_date2 + trail)
        last_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s' % (str(date)+ '_' + model_date2 + trail)
        
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        index_list = pd.read_pickle('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/rank_index/%s_60000_25_75/%s.pkl'%(cat, str(next_tday)))
        gen_history_signal_values_2(days_list[-1], model_path, index_list, save_path)
        del save_path
        

        del days_list
        del model_date
        del next_tday
        del start_date
        
        if os.path.exists(last_path):
            from shutil import rmtree
            rmtree(last_path)
flag_path_success = flag_path + str(date) + '_norm2_generation.success'
with open(flag_path_success,'w') as file:
    pass 