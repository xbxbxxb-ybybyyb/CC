# -*- coding: utf-8 -*-
"""
Created on Fri Dec 23 09:27:56 2022

@author: appadmin
"""


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

version_list = [ 'if_v7_crn', 'if_v7c']

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS_sim/'

################## model setting ###################
# manual update for each model update date

######## regular setting #######
model_date_dict = {'if_v7c':'20221125_if_if_v7c',
                   'if_v7_crn':'20221125_if_if_v7_crn',
 }


version_ticker_dict = {'if_v7_crn':'IF.CFE', 'if_v7c':'IF.CFE'}
model_date_use_dict = {
                       'if_v7_crn':'%s'%(model_date_dict['if_v7_crn']),
                       'if_v7c':'%s'%(model_date_dict['if_v7_crn'])
                       }
                    

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
    
def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_ic_factors.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_if_factors.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_if_zscore.success'
    path5 = flag_rootpath + str(date) + '/' + 'MODEL.success'
    path6 = flag_rootpath + str(date) + '/' + '%s_model.success'%str(date)
    return (os.path.exists(path5) and os.path.exists(path6))


for datee in date_list:
    
    date = str(datee)
    print(date)
    #flag_path = flag_rootpath + str(date) + '/'
    #if not os.path.exists(flag_path):
    #    os.makedirs(flag_path)


    #print('------wait data flag')
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')

    for version in version_list:
    #if 'IC.CFE' in contract_list:
        if ('ic' in version.lower()) and ('short' not in version.lower()):
            cat = '_ic'  
            model_date = str(model_date_dict[version])# + cat
            model_date2 = model_date# + '_' + version
            
            # gen factors
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-20)[0].strftime('%Y%m%d')
            days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

            factorlib_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_raw/'
            save_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/trade_files/%s/historyFactor' % (next_tday + '_' + model_date2 + trail)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            #for d in days_list:
            #    gen_history_factor_values(d, factorlib_path, save_path)

            Parallel(n_jobs= -1)(delayed(gen_history_factor_values)(d, factorlib_path, save_path) for d in days_list)
            del save_path
            
            # gen models
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-29)[0].strftime('%Y%m%d')
            days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

            model_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw/%s' % (str(model_date), str(date))
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (next_tday + '_' + model_date2 + trail)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            for d in days_list:
                gen_history_signal_values(d, model_path, save_path)  
            Parallel(n_jobs= -1)(delayed(gen_history_signal_values)(d, model_path, save_path) for d in days_list)
            del save_path

            norm_factorlib_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_norm/'
            dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
            save_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/trade_files/%s/historyNormFactor' % (next_tday + '_' + model_date2 + trail)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            # 生成文件
            gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
            gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
            del factorlib_path
            del norm_factorlib_path
            del save_path
            del model_path
            del days_list
            del model_date
            del cat


    ####################################################### IF ############################################################### 

        elif ('if' in version.lower()) and ('short' not in version.lower()):
            cat = '_if'
            model_date = str(model_date_dict[version])# + cat
            
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date_if = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
            days_list_if = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date_if, date)]

            factorlib_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_raw/'
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyFactor' % (str(next_tday) + '_' + model_date + trail_if)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            #for d in days_list_if:
            #    gen_history_factor_values(d, factorlib_path, save_path)
            Parallel(n_jobs= -1)(delayed(gen_history_factor_values)(d, factorlib_path, save_path) for d in days_list_if)
            del save_path

            # gen models
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-29)[0].strftime('%Y%m%d')
            days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

            model_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw/%s' % (str(model_date), str(date))
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (str(next_tday) + '_' + model_date + trail_if)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            #for d in days_list:
            #    gen_history_signal_values(d, model_path, save_path)    
            Parallel(n_jobs= -1)(delayed(gen_history_signal_values)(d, model_path, save_path) for d in days_list)
            del save_path

            norm_factorlib_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'
            dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyNormFactor' % (str(next_tday) + '_' + model_date + trail_if)
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            # 生成文件
            gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
            gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
            del factorlib_path
            del norm_factorlib_path
            del save_path
            del model_path
            del days_list
            del model_date
            del cat

        elif ('ic' in version.lower()) and ('short' in version.lower()):
            cat = '_ic'
            model_date = str(model_date_dict[version])# + cat + '_short'
            #print(model_date)
            
            # gen factors
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
            days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyFactor' % (next_tday + '_' + model_date)
            factorlib_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_raw/'

            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            #for d in days_list:
            #    gen_history_factor_values(d, factorlib_path, save_path)

            Parallel(n_jobs= -1)(delayed(gen_history_factor_values)(d, factorlib_path, save_path) for d in days_list)
            del save_path
            

            # gen models
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-29)[0].strftime('%Y%m%d')
            days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

            model_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw/%s' % (str(model_date), str(date))
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (next_tday + '_' + model_date)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            #for d in days_list:
            #    gen_history_signal_values(d, model_path, save_path)  
            Parallel(n_jobs= -1)(delayed(gen_history_signal_values)(d, model_path, save_path) for d in days_list)
            del save_path

            norm_factorlib_path = '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_norm/'
            dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
            
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyNormFactor' % (next_tday + '_' + model_date)
            
            if not os.path.exists(save_path):
                os.makedirs(save_path)
            # 生成文件
            gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
            gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
            
            del factorlib_path
            del norm_factorlib_path
            del save_path
            del model_path
            del days_list
            del model_date
            del cat
        else:
            pass

lm = link.LinkMessage()
lm.sendMessage('PROD - GEN MODEL/FACTORS FINISHED!')
del lm

#flag_path = flag_rootpath + str(edate) + '/'
#flag_path_success = flag_path + str(edate) + '_GEN_MODEL_FACTORS.success'
#with open(flag_path_success,'w') as file:
#    pass 


from multifactor.data.utils import *
import multifactor.utility.dt as udt
from xquant.xqutils.helper import link
import pandas as pd
import os



_,edate,_ = check_update_date()

# ！！！ 修改实盘因子配置文件时需要改如下路径

if_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_V4.0.1.json'

trade_files_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/'

next_tday = udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')

wrong_reason = []

model_list = []
for model_name in model_date_dict.keys():
    model_list.append('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/' + model_date_dict[model_name] + '/')


    # 检查ICIF的因子文件
    
    if 'if' in model_name.lower():
        kind = 'if'
    elif 'ic' in model_name.lower():
        kind = 'ic'
    elif 'ih' in model_name.lower():
        kind = 'ih'
    else:
        kind = 'im'
    _json = ic_factor_json if kind == 'ic' else if_factor_json
    _suffix = '_all' if kind  == 'ic' else '_all_if'
    datajson = pd.read_json(_json)
    json_factors = datajson.FactorName.tolist()
    if len(json_factors) != len(set(json_factors)):
        wrong_reason.append('%s json wrong' % kind)
    rawfactor_path = os.path.join('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s_%s/historyFactor/'%(str(next_tday), model_date_dict[model_name]))
    if len(os.listdir(rawfactor_path)) != 62:
        wrong_reason.append('%s trade files raw num wrong' % kind)
    for x in os.listdir(rawfactor_path):
        history_factors = []
        with open(os.path.join(rawfactor_path, x),'r') as f:
            line = f.readline()
            while line:
                line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                history_factors.append(line['FactorName'])
                if len(line['Values']) != 237:
                    wrong_reason.append('%s factor raw lenth wrong' % (str(os.path.join(rawfactor_path, x)) + line['FactorName']))
                line = f.readline()
        if len(set(json_factors) - set(history_factors)) != 0:
            wrong_reason.append('%s trade files raw factor wrong' % kind)

    normfactor_path = os.path.join('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s_%s/historyNormFactor/'%(str(next_tday), model_date_dict[model_name]))
    if len(os.listdir(normfactor_path)) != 1:
        wrong_reason.append('%s trade files norm factor num wrong' % kind)
    norm_factors = []
    with open(os.path.join(normfactor_path, str(edate)),'r') as f:
        line = f.readline()
        while line:
            line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
            norm_factors.append(line['FactorName'])
            if len(line['Values']) != 237:
                wrong_reason.append('%s factor norm lenth wrong' % (str(os.path.join(rawfactor_path, x)) + line['FactorName']))
            line = f.readline()
    if len(set(json_factors) - set(norm_factors)) != 0:
        wrong_reason.append('%s trade files norm factor wrong' % kind)      


for model_path in model_list:
        model_name = model_path.split('/')[-2]
        model_file_path = os.path.join(trade_files_path, str(next_tday) + '_' + model_name, 'historySignal')
        if len(os.listdir(model_file_path)) != 30:
            wrong_reason.append(' num wrong' % model_file_path)
        for x in os.listdir(model_file_path):
            with open(os.path.join(model_file_path, x),'r') as f:
                line = f.readline()
                while line:
                    line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                    if len(line['Values']) != 237:
                        wrong_reason.append('%s model value lenth wrong' % os.path.join(model_file_path, x))
                    line = f.readline()

from xquant.xqutils.helper import link                  

def link_send_message(message):
    
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)
    
    
    
if len(wrong_reason) > 0:
        link_send_message('trade files error!!!!!')
        link_send_message(str(wrong_reason))
        print(wrong_reason)
else:
    link_send_message('trade files fine')
