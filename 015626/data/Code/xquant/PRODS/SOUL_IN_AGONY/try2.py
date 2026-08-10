

from bisect import bisect_left
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
import sys
import subprocess
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
            #print(full_name)
            data = pd.read_pickle(full_name)
            col_set = set(data.columns)

            dest_data = data[data.index>date_str]
            dest_data = dest_data[dest_data.index < to_date_str]
            for col in list(dest_data.columns):
                dest_data[col] = dest_data[col].astype('float64')
                signal_value_list = list(dest_data[col].values)
                #print(col + ': ' + str(len(signal_value_list)))
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
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_if_zscore.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)




for date1 in [20240830, 20240902, 20240903, 20240904, 20240926, 20240927]:
    date = str(date1)
    for model_date in ['20240628_ic_ic_v7unifac_crn', '20240628_ic_ic_v7unifac_crn_50', '20240628_ic_ic_v7unifac_crn_55']:#['20240628_ic_ic_v7unifac_50', '20240628_ic_ic_v7unifac_55', '20240628_im_im_v1unifac_50', '20240628_im_im_v1unifac_55', '20240628_if_if_v7c_50', '20240628_if_if_v7c_55']:        
        #model_date = str(model_date_dict[version])# + cat
        model_date2 = model_date# + '_' + version

        # gen models
        next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
        start_date = udt.get_trading_day_offset(date,-30)[0].strftime('%Y%m%d')
        days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]
        
        model_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw/%s' % (str(model_date), str(date))
        print(model_path)
        if ('_50' in model_date) or ('_55' in model_date):
            save_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (next_tday + '_' + model_date2 + trail)
        else:
            save_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (next_tday + '_' + model_date2 + '_00' + trail)
        if not os.path.exists(save_path):
            os.makedirs(save_path)
            
        # 生成文件
        Parallel(n_jobs= -1)(delayed(gen_history_signal_values)(d, model_path, save_path) for d in days_list)
        
        del save_path
        del model_path
        del days_list
        del model_date