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

sim = False

contract_list = ['IC.CFE', 'IF.CFE']

if sim == True:
    trail = '_sim'
else:
    trail = ''

code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
print(code_base)
sys.path.insert(0, os.path.dirname(code_base))
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
from sklearn.preprocessing import StandardScaler
from keras.models import load_model
from multiprocessing import Pool
import multifactor.utility.dt as udt


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
            print('begin to get ' + factor_name + ' history value')
            if (col_set.__contains__('index')):
                dest_data = data[data['index']>date_str]
                dest_data = dest_data[dest_data['index'] < to_date_str]
                dest_data[factor_name] = dest_data[factor_name].astype('float64')
                factor_value_list = list(dest_data[factor_name].values)
                print(factor_name + ': ' + str(len(factor_value_list)))
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
                print(factor_name + ': ' + str(len(factor_value_list)))
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
            print(full_name)
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
    
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'    
def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_ic_factors.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_if_factors.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_model.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3)

#_,date,_ = check_update_date()
_,eedate,date_list = check_update_date()
date = str(eedate)

flag_path = flag_rootpath + str(date) + '/'
if not os.path.exists(flag_path):
    os.makedirs(flag_path)
flag_path_start = flag_path + str(date) + '_gen_factors_and_model.start'
with open(flag_path_start,'w') as file:
    pass 

print('------wait data flag')
while True:
    if minute_flag_check(date):
        break
    time.sleep(60)
print('flag check finished!')

if 'IC.CFE' in contract_list:

    # gen factors
    next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
    start_date = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
    days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

    factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_ever%s/minute_raw/'%trail
    save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s_all%s/historyFactor' % (next_tday, trail)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 生成文件
    #for d in days_list:
    #    gen_history_factor_values(d, factorlib_path, save_path)
    
    Parallel(n_jobs= -1)(delayed(gen_history_factor_values)(d, factorlib_path, save_path) for d in days_list)
    del save_path
    

    norm_factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_ever%s/minute_norm/'%trail
    dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
    save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s_all%s/historyNormFactor' % (next_tday, trail)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 生成文件
    gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
    gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
    del factorlib_path
    del norm_factorlib_path
    del save_path
    #del model_path
    del days_list

if 'IF.CFE' in contract_list:
    # gen factors
    next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
    start_date = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
    days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

    factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever%s/minute_raw/'%trail
    save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s_all_if%s/historyFactor' % (next_tday, trail)
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    # 生成文件
    #for d in days_list:
    #    gen_history_factor_values(d, factorlib_path, save_path)
    
    Parallel(n_jobs= -1)(delayed(gen_history_factor_values)(d, factorlib_path, save_path) for d in days_list)
    del save_path
    

    norm_factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever%s/minute_norm/'%trail
    dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
    save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s_all_if%s/historyNormFactor' % (next_tday, trail)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    # 生成文件
    gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
    gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
    del factorlib_path
    del norm_factorlib_path
    del save_path
    #del model_path
    del days_list
    
from xquant.xqutils.helper import link    
lm = link.LinkMessage()
lm.sendMessage('PROD - GEN MODEL/FACTORS FINISHED!')
del lm 
