
import sys
import subprocess

# implement pip as a subprocess:
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'onnx'])
subprocess.check_call([sys.executable, '-m', 'pip', 'install', 
'onnxruntime'])

import onnx
import onnxruntime as ort

import os
import pickle
import numpy as np
import pandas as pd
import bottleneck as bk
import onnx
import onnxruntime as ort
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from multifactor.data.utils import *
from joblib import Parallel, delayed

full_date = '20230331'
number_of_models = 10

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

model_name_list = ['%s_if_if_v8_crn'%full_date]
######## regular setting #######
model_date_dict = {'if_v7c':'%s_if_if_v7c'%full_date,
                   'if_v7_crn':'%s_if_if_v7_crn_new'%full_date,                  
                   'ic_v7unifac': '%s_ic_ic_v7unifac'%full_date,
                   'ic_v7unifac_crn': '%s_ic_ic_v7unifac_crn_new'%full_date,
                   'ic_v7c': '%s_ic_ic_v7c'%full_date,
 }
_, __, update_date_list = check_update_date()

def calc(ud, model_name):
    # set update date
    update_date = str(ud)
    print('update_date: {}'.format(update_date))

    # set model dir and output dir
    
    model_trade_dir = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_trade/%s'%(model_name, model_name)
    model_value_dir = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value'%model_name

    assert os.path.exists('{}/model_raw_itr'.format(model_value_dir))
    assert os.path.exists('{}/model_raw'.format(model_value_dir))
    assert os.path.exists('{}/model_norm'.format(model_value_dir))

    # other configuration
    model_name_list = ['crn_cla', 'crn_reg']
    pred_time_list = [1, 5, 10]
    
    
    if '_if_' in model_name.lower():
        model_num = 10
        factor_dir_list = [
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v8_1/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm'
        ]
        
    if '_ic_' in model_name.lower():
        model_num = 10
        factor_dir_list = [
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v8_1/minute_norm',
        ]
        
    if '_im_' in model_name.lower():
        model_num = 25
        factor_dir_list = [
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/im_unifac_ever/minute_norm',
            '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v8_1/minute_norm',
        ]
        
    # load data
    str_date = (pd.Timestamp(update_date) - pd.Timedelta(15, 'day')).strftime('%Y%m%d')
    end_date = update_date
    factor_list = []
    for factor_dir in factor_dir_list:
        print('fetch factor from {}'.format(factor_dir))
        factor_all = fetch_factor(factor_dir)
        factor_all = factor_all[str_date:end_date]
        factor_list.append(factor_all)
    factor_all = merge_factor(factor_list)
    factor_all = fill_inf_and_nan(factor_all)

    # calculate new value
    for model_name in model_name_list:
        for pred_time in pred_time_list:
            update_raw_itr(factor_all, model_trade_dir, model_value_dir, update_date, model_name, pred_time, num_models=number_of_models)

    # update raw value
    for model_name in model_name_list:
        update_raw(model_value_dir, update_date, model_name, pred_time_list)

    # update norm value
    for model_name in model_name_list:
        update_norm(model_value_dir, update_date, model_name, rank_period=4800)
    
    holder = pd.DataFrame()
    for model_name in model_name_list:
        temp = pd.read_pickle('{}/model_norm/{}/{}.pkl'.format(model_value_dir, update_date, model_name))
        holder = pd.concat([holder, temp], axis = 1)
    ts_rank(holder.mean(axis = 1), 2400).to_pickle('{}/model_norm/{}/{}.pkl'.format(model_value_dir, update_date, 'pred_comb2'))   
    return None


def update_raw_itr(factor_all, model_trade_dir, model_value_dir, update_date, model_name, pred_time, num_models):
    # make prediction
    prediction_all = {}
    for model_idx in range(num_models):
        # load model
        model_path = '{}/{}/{}_{}_{}.onnx'.format(model_trade_dir, model_name, model_name, pred_time, model_idx)
        model_onnx = onnx.load(model_path)
        onnx.checker.check_model(model_onnx)
        model_onnx = model_onnx.SerializeToString()
        ort_sess = ort.InferenceSession(model_onnx)

        # load input list
        input_path = '{}/{}/{}_{}_{}.csv'.format(model_trade_dir, model_name, model_name, pred_time, model_idx)
        input_list = pd.read_csv(input_path)
        input_list = input_list['factor_name'].to_list()

        # prepare model input
        x_pd = factor_all[input_list]
        input_shape = ort_sess.get_inputs()[0].shape
        if len(input_shape) == 2:
            pred_index = x_pd.index
            pred_input = x_pd.values
        elif len(input_shape) == 3:
            time_step = input_shape[1]
            pred_index = x_pd.iloc[time_step - 1:].index
            pred_input = transform_2d_to_3d(x_pd.values, time_step)
        else:
            print('the dimension of x is not 2 or 3')
            raise Exception

        # predict
        y_np = []
        for t in range(pred_input.shape[0]):
            x_np = pred_input[t:t + 1]
            res = ort_sess.run(None, {ort_sess.get_inputs()[0].name: x_np.astype(np.float32)})
            y_np.append(res[0])
        y_np = np.concatenate(y_np, axis=0)
        y_pd = pd.Series(y_np, index=pred_index)

        prediction_all[model_idx] = y_pd[update_date:update_date]
    prediction_all = pd.DataFrame(prediction_all)

    # save prediction
    make_dir('{}/model_raw_itr/{}'.format(model_value_dir, update_date))
    pred_path = '{}/model_raw_itr/{}/{}_{}.pkl'.format(model_value_dir, update_date, model_name, pred_time)
    print('save prediction to {}'.format(pred_path))
    save_pickle(prediction_all, pred_path)
    return None


def update_raw(model_value_dir, update_date, model_name, pred_time_list):
    # average
    pred_new = {}
    for pred_time in pred_time_list:
        pred_path = '{}/model_raw_itr/{}/{}_{}.pkl'.format(model_value_dir, update_date, model_name, pred_time)
        pred_all = load_pickle(pred_path)
        pred_avg = pred_all.mean(axis=1)
        pred_new['{}_{}'.format(model_name, pred_time)] = pred_avg
    pred_new = pd.DataFrame(pred_new)

    # concatenate
    latest_date = None
    date_list = os.listdir('{}/model_raw'.format(model_value_dir))
    date_list = sorted(date_list, reverse=False)
    for date in date_list:
        if date < update_date:
            latest_date = date
    if latest_date is None:
        print('missing historical raw value')
        raise Exception
    print('latest_date: {}, update_date: {}'.format(latest_date, update_date))
    pred_path = '{}/model_raw/{}/{}.pkl'.format(model_value_dir, latest_date, model_name)
    pred_old = load_pickle(pred_path)
    pred_cat = pd.concat([pred_old, pred_new], axis=0)

    # save
    make_dir('{}/model_raw/{}'.format(model_value_dir, update_date))
    pred_path = '{}/model_raw/{}/{}.pkl'.format(model_value_dir, update_date, model_name)
    print('save raw value to {}'.format(pred_path))
    save_pickle(pred_cat, pred_path)
    return None


def update_norm(model_value_dir, update_date, model_name, rank_period):
    # raw value
    signal_path = '{}/model_raw/{}/{}.pkl'.format(model_value_dir, update_date, model_name)
    signal_raw = load_pickle(signal_path)

    # norm value
    signal_norm = ts_rank(signal_raw, rank_period)
    signal_norm_avg = signal_norm.mean(axis=1)
    signal_norm_avg = pd.DataFrame(signal_norm_avg, columns=[model_name])

    # save
    make_dir('{}/model_norm/{}'.format(model_value_dir, update_date))
    signal_path = '{}/model_norm/{}/{}.pkl'.format(model_value_dir, update_date, model_name)
    print('save norm value to {}'.format(signal_path))
    save_pickle(signal_norm_avg, signal_path)
    return None


def make_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
    return None


def save_pickle(data, path):
    with open(path, mode='wb') as file:
        pickle.dump(data, file, protocol=3)
    return None


def load_pickle(path):
    with open(path, mode='rb') as file:
        data = pickle.load(file)
    return data


def fetch_factor(factor_dir):
    factor_list = []
    file_name_list = os.listdir(factor_dir)
    def read_factors(file_name, factor_dir = factor_dir):
    #for file_name in file_name_list:
        data_path = '{}/{}'.format(factor_dir, file_name)
        factor = pd.DataFrame(pd.read_hdf(data_path))
        return factor
        #factor_list.append(factor)
    #with Pool(24) as pool:
    #    factor_list = pool.map(read_factors, file_name_list)
    factor_list = Parallel(n_jobs= -1)(delayed(read_factors)(file_name) for file_name in file_name_list)
    factor_all = pd.concat(factor_list, axis=1, join='outer')
    # sort by factor name
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique
    # check time: 09:30 ~ 11:29, 13:00 ~ 14:56, 120 + 117 = 237
    factor_all = factor_all.between_time(start_time='09:30', end_time='14:56')
    assert factor_all.shape[0] % 237 == 0
    return factor_all


def merge_factor(factor_list):
    factor_all = pd.concat(factor_list, axis=1, join='outer')
    # sort by factor name
    factor_all = factor_all.sort_index(axis=1, ascending=True)
    assert factor_all.columns.is_unique
    # check time: 09:30 ~ 11:29, 13:00 ~ 14:56, 120 + 117 = 237
    factor_all = factor_all.between_time(start_time='09:30', end_time='14:56')
    assert factor_all.shape[0] % 237 == 0
    return factor_all


def fill_inf_and_nan(x):
    x = x.replace([np.inf, -np.inf], np.nan)
    x = x.fillna(0.0)
    return x


def transform_2d_to_3d(x_2d, time_step):
    x_len = x_2d.shape[0]
    if x_len < time_step:
        print('the length of x is shorter than time_step')
        raise Exception
    x_3d = []
    for t in range(x_len - time_step + 1):
        xt = x_2d[t:t + time_step, :]
        x_3d.append(xt)
    x_3d = np.array(x_3d)
    return x_3d


def ts_rank(data, d):
    if d == 1:
        output = data
    else:
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0), index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_rank(data, window=d, min_count=int(d / 2), axis=0), index=data.index, name=data.name)
        elif isinstance(data, np.ndarray):
            output = bk.move_rank(data, window=d, min_count=int(d / 2), axis=0)
        else:
            output = None
    return output

def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + 'if_factors.success' 
    path2 = flag_rootpath + str(date) + '/' + 'ih_factors.success' 
    path3 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_if_zscore.success'
    return os.path.exists(path1) and os.path.exists(path3) and os.path.exists(path4)



    
    
for date in update_date_list:
    while True:
        if minute_flag_check(date):
            break
        time.sleep(60)
    print('flag check finished!')
    for model_name in model_name_list:
        calc(date, model_name)




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

version_list = [ 'if_v7_crn', 'ic_v7unifac_crn']

flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/'

################## model setting ###################
# manual update for each model update date


version_ticker_dict = {'if_v7_crn':'IF.CFE', 'if_v7c':'IF.CFE', 'ic_v7unifac_crn': 'IC.CFE', 'ic_v7unifac': 'IC.CFE'}
model_date_use_dict = {
                       'if_v7_crn':'%s'%(model_date_dict['if_v7_crn']),
                       'if_v7c':'%s'%(model_date_dict['if_v7_crn']),
                       'ic_v7unifac_crn':'%s'%(model_date_dict['ic_v7unifac_crn']),
                       'ic_v7unifac':'%s'%(model_date_dict['ic_v7unifac']),
                       'ic_v7c':'%s'%(model_date_dict['ic_v7c'])
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
    



for datee in date_list:
    
    date = str(datee)
    print(date)

    print('START')

    for version in version_list:
    #if 'IC.CFE' in contract_list:
        if ('_ic_' in model_date_dict[version].lower()) and ('unifac' in model_date_dict[version].lower()):
            cat = '_ic'  
            model_date = str(model_date_dict[version])# + cat
            model_date2 = model_date# + '_' + version
            
            
            # gen models
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-30)[0].strftime('%Y%m%d')
            days_list = [x.strftime('%Y-%m-%d') for x in udt.get_trading_date_range(start_date, date)]

            model_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw/%s' % (str(model_date), str(date))
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historySignal' % (next_tday + '_' + model_date2 + trail)
            if not os.path.exists(save_path):
                os.makedirs(save_path)

            # 生成文件
            #for d in days_list:
            #    gen_history_signal_values(d, model_path, save_path)  
            Parallel(n_jobs= -1)(delayed(gen_history_signal_values)(d, model_path, save_path) for d in days_list)
            del save_path

            norm_factorlib_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/ic_unifac_ever/minute_norm/'
            dummies_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/dummies/minute_norm/'
            save_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/%s/historyNormFactor' % (next_tday + '_' + model_date2 + trail)
            #if not os.path.exists(save_path):
            #    os.makedirs(save_path)
            # 生成文件
            #print(len(os.listdir(norm_factorlib_path)))
            #gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
            #gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
            
            del save_path
            del model_path
            del days_list
            del model_date
            del cat


    ####################################################### IF ############################################################### 

        if ('_if_' in model_date_dict[version].lower()) and ('short' not in model_date_dict[version].lower()):
            cat = '_if'
            model_date = str(model_date_dict[version])# + cat
            

            # gen models
            next_tday = udt.get_trading_day_offset(date,1)[0].strftime('%Y%m%d')
            start_date = udt.get_trading_day_offset(date,-30)[0].strftime('%Y%m%d')
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
            #if not os.path.exists(save_path):
            #    os.makedirs(save_path)
            # 生成文件
            #gen_history_factor_values(days_list[-1], norm_factorlib_path, save_path)
            #gen_history_factor_values(days_list[-1], dummies_path, save_path, write_type = 'a+')
            
            del save_path
            del model_path
            del days_list
            del model_date
            del cat

        
        else:
            pass

lm = link.LinkMessage()
lm.sendMessage('NEW - GEN MODEL/FACTORS FINISHED!')
del lm

flag_path_success = flag_rootpath + str(date) + '/' + 'trade_files.success'
with open(flag_path_success,'w') as file:
    pass

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
ic_factor_json = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/factor_definition/factor_definition_set_V4.0.1_icuf.json'

trade_files_path = '/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/trade_files/'

next_tday = udt.get_trading_day_offset(edate,1)[0].strftime('%Y%m%d')

wrong_reason = []

model_list = []
for model_name in version_list:
    model_list.append('/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/model/model_trade/' + model_date_dict[model_name] + '/')

from xquant.xqutils.helper import link                  

def link_send_message(message):
    
    lm = link.LinkMessage()
    lm.sendMessage(message)
    del(lm)    

for model_path in model_list:
    model_name = model_path.split('/')[-2]
    model_file_path = os.path.join(trade_files_path, str(next_tday) + '_' + model_name, 'historySignal')
    if len(os.listdir(model_file_path)) != 31:
        wrong_reason.append(' num wrong %s' % model_file_path)
    for x in os.listdir(model_file_path):
        with open(os.path.join(model_file_path, x),'r') as f:
            line = f.readline()
            if len(line) == 0:
                wrong_reason.append('%s empty file' % os.path.join(model_file_path, x))
                link_send_message('FUCK EMPTY FILES!')
                link_send_message(model_path.split('/')[-1])
            while line:
                line = eval(line.replace('NaN','9999').replace('Infinity','9999'))
                if len(line['Values']) != 237:
                    wrong_reason.append('%s model value lenth wrong' % os.path.join(model_file_path, x))
                line = f.readline()


if len(wrong_reason) > 0:
    link_send_message('crn:   trade files error!!!!!')
    link_send_message(str(wrong_reason))
    print(wrong_reason)
else:
    link_send_message('crn:   trade files fine')




flag_path_success = flag_rootpath + str(date) + '/' + 'MODEL.success'
with open(flag_path_success,'w') as file:
    pass
