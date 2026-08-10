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

#version_list = ['ic_short_v1']
version_list = ['ic_v7c', 'ic_short_v3c', 'if_v6nl']
model_date_dict = {'ic_prod_v6':'20220715_ic_ic_prod_v6_fix',
                   'if_prod_v5_add':'20220624_if_if_prod_v5_add2',
                   'ic_short_v1':'20221021_ic_ic_short_v2',
                   'ic_trade_v1':'20220513_ic_trade_v1_ic2',
                   'if_v6nl':'20221125_if_if_v6nl',
                   'ic_v7c':'20221125_ic_ic_v7c',
                   'ic_short_v3c':'20221125_ic_ic_short_v3c'}


################## model setting ###################
# manual update for each model update date

######## regular setting #######
version_ticker_dict = {'ic_v7c':'IC.CFE','if_prod_v5_add':'IF.CFE','ic_short_v1':'IC.CFE','ic_trade_v1':'IC.CFE','if_v6nl':'IF.CFE'}
model_date_use_dict = {'ic_trade_v1':'%s'%(model_date_dict['ic_trade_v1']),
                       'ic_v7c':'%s'%(model_date_dict['ic_v7c']),
                       'if_prod_v5_add':'%s'%(model_date_dict['if_prod_v5_add']),
                       'ic_short_v1':'%s'%(model_date_dict['ic_short_v1']),
                       'if_v6nl':'%s'%(model_date_dict['if_v6nl'])}
ts_pct_win_dict = {'ic_trade_v1':20*240,'ic_v7c':20*240,'if_prod_v5_add':20*240,'ic_short_v1':5*240,'if_v6nl':20*240} # sub model raw to norm pct_win
ts_pct_win_dict2 = {'ic_trade_v1':10*240,'ic_v7c':10*240,'if_prod_v5_add':10*240,'ic_short_v1':5*240,'if_v6nl':10*240} # model stack pct_win
model_list_dict = {'ic_trade_v1':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'ic_v7c':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'if_prod_v5_add':['lasso_reg','lr_cla','et_cla','lgbm_cla','lstm_cla','mlp_reg'],
                   'ic_short_v1':['rff_cla','rfe_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'ic_v7c':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'if_v6nl':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg']}
fac_path_dict= {'ic_trade_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/trade_v1/minute_norm',
                'ic_v7c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_prod_v7_2/minute_norm',
                'if_prod_v5_add':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v5/minute_norm',
                'ic_short_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_short_v2/minute_norm',
                'if_v6nl':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v6/minute_norm'}
fac_desc_raw_path_dict = {'ic_trade_v1':'',
                          'ic_v7c':'',
                          'if_prod_v5_add':'',
                          'ic_short_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear/minute_norm',
                          'if_v6nl':''}                 
fac_desc_norm_path_dict = {'ic_trade_v1':'',
                           'ic_v7c':'',
                           'if_prod_v5_add':'',
                           'ic_short_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
                           'if_v6nl':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm'}                 

comb2_model_list =['mlp_reg','lstm_cla']
model_list_extra = ['rff_cla','rfe_cla']

long_list = [10,20,30]
short_list = [1,5,10] 
hpr_spec_dict_all = {'ic_trade_v1':{i:long_list for i in model_list_dict['ic_trade_v1']},
                    'ic_v7c':{i:long_list for i in model_list_dict['ic_v7c']},
                    'if_prod_v5_add':{**{i:long_list for i in ['lasso_reg','lr_cla','et_cla','lstm_cla','mlp_reg']},
                                      **{i:short_list for i in ['lgbm_cla']}},
                    'ic_short_v1':{**{i:long_list for i in ['lstm_cla','et_cla']},
                                   **{i:short_list for i in ['rff_cla','rfe_cla','lgbm_cla','lgbm_reg','mlp_reg']}},
                    'if_v6nl':{**{i:long_list for i in ['lstm_cla','et_cla','lr_cla']},
                               **{i:short_list for i in ['lasso_reg','lgbm_cla','lgbm_reg','mlp_reg']}}}    
with_desc_dict = {'ic_trade_v1':False,'ic_v7c':False,'if_prod_v5_add':False,'ic_short_v1':True,'if_v6nl':False} # nonlinear_raw_factor # for cc rfe rff only
with_desc_norm_dict = {'ic_trade_v1':False,'ic_v7c':False,'if_prod_v5_add':False,'ic_short_v1':True,'if_v6nl':True} # nonlinear_factor_norm

time_step_dict = {**{i:30 for i in ['ic_trade_v1','ic_v7c','if_prod_v5_add','ic_short_v1']},
                  **{i:10 for i in ['if_v6nl']}}
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
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'    
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
    
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'    
def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + str(date) + '_ic_factors.success'
    path2 = flag_rootpath + str(date) + '/' + str(date) + '_if_factors.success'
    path3 = flag_rootpath + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = flag_rootpath + str(date) + '/' + str(date) + '_if_zscore.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)




date = str(eedate)

flag_path = flag_rootpath + str(date) + '/'
if not os.path.exists(flag_path):
    os.makedirs(flag_path)


print('------wait data flag')
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
        flag_path_start = flag_path + str(date) + '_gen_factors_and_model_%s.start'%model_date
        with open(flag_path_start,'w') as file:
            pass 

        # gen factors
        next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
        start_date = udt.get_trading_day_offset(date,-20)[0].strftime('%Y%m%d')
        days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

        factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_raw/'
        save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyFactor' % (next_tday + '_' + model_date2 + trail)
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

        norm_factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_norm/'
        dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
        save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyNormFactor' % (next_tday + '_' + model_date2 + trail)
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
        flag_path_start = flag_path + str(date) + '_gen_factors_and_model_%s.start'%model_date
        with open(flag_path_start,'w') as file:
            pass 
        next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
        start_date_if = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
        days_list_if = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date_if, date)]

        factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_raw/'
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

        norm_factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_ever/minute_norm/'
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
        flag_path_start = flag_path + str(date) + '_gen_factors_and_model_%s.start'%model_date
        with open(flag_path_start,'w') as file:
            pass 

        # gen factors
        next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
        start_date = udt.get_trading_day_offset(date,-61)[0].strftime('%Y%m%d')
        days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

        save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyFactor' % (next_tday + '_' + model_date)
        factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_raw/'

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

        norm_factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_ever/minute_norm/'
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

flag_path = flag_rootpath + str(eedate) + '/'
flag_path_success = flag_path + str(eedate) + '_GEN_MODEL_FACTORS.success'
with open(flag_path_success,'w') as file:
    pass 
