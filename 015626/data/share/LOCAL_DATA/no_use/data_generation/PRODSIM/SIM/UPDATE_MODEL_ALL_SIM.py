
# -*- coding: utf-8 -*-
"""
Created on Fri May  6 14:09:50 2022

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
import sys
import subprocess



version_list = ['if_v7c']
model_date_dict = {'ic_prod_v6':'20220715_ic_ic_prod_v6_fix',
                   'if_prod_v5_add':'20220624_if_if_prod_v5_add2',
                   'ic_short_v1':'20221021_ic_ic_short_v2',
                   'ic_trade_v1':'20220513_ic_trade_v1_ic2',
                   'if_v6nl':'20221125_if_if_v6nl',
                   'ic_v7c':'20221125_ic_ic_v7c',
                   'ic_short_v3c':'20221125_ic_ic_short_v3c',
                   'if_v7c':'20221125_if_if_v7c'}


################## model setting ###################
# manual update for each model update date

######## regular setting #######
roll_name_dict = {'ic_prod_v6':'_r240','if_prod_v5_add':'_r240','ic_short_v1':'_r720',
                  'ic_trade_v1':'_r240','if_v6nl':'_r720','ic_v7c':'_r720', 'ic_short_v3c':'_r720',
                  'if_v7c':'_r720'}

version_ticker_dict = {'ic_prod_v6':'IC.CFE','if_prod_v5_add':'IF.CFE','ic_short_v1':'IC.CFE',
                       'ic_trade_v1':'IC.CFE','if_v6nl':'IF.CFE','ic_v7c':'IC.CFE','ic_short_v3c':'IC.CFE',
                       'if_v7c':'IF.CFE'}

model_date_use_dict = {'ic_trade_v1':'%s'%(model_date_dict['ic_trade_v1']),
                       'ic_prod_v6':'%s'%(model_date_dict['ic_prod_v6']),
                       'if_prod_v5_add':'%s'%(model_date_dict['if_prod_v5_add']),
                       'ic_short_v1':'%s'%(model_date_dict['ic_short_v1']),
                       'if_v6nl':'%s'%(model_date_dict['if_v6nl']),
                       'ic_v7c':'%s'%(model_date_dict['ic_v7c']),
                       'ic_short_v3c':'%s'%(model_date_dict['ic_short_v3c']),
                       'if_v7c':'%s'%(model_date_dict['if_v7c'])}

ts_pct_win_dict = {'ic_trade_v1':20*240,'ic_prod_v6':20*240,'if_prod_v5_add':20*240,
                   'ic_short_v1':5*240,'if_v6nl':20*240,'ic_v7c':20*240,'ic_short_v3c':20*240,
                   'if_v7c':20*240} # sub model raw to norm pct_win

ts_pct_win_dict2 = {'ic_trade_v1':10*240,'ic_prod_v6':10*240,'if_prod_v5_add':10*240,
                    'ic_short_v1':5*240,'if_v6nl':10*240,'ic_v7c':10*240,'ic_short_v3c':10*240,
                    'if_v7c':10*240} # model stack pct_win

model_list_dict = {'ic_trade_v1':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'ic_prod_v6':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'if_prod_v5_add':['lasso_reg','lr_cla','et_cla','lgbm_cla','lstm_cla','mlp_reg'],
                   'ic_short_v1':['rff_cla','rfe_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'ic_prod_v6':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'if_v6nl':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'ic_v7c':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'ic_short_v3c':['et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg'],
                   'if_v7c':['lasso_reg','lr_cla','et_cla','lgbm_cla','lgbm_reg','lstm_cla','mlp_reg','mlp_cla']}

fac_path_dict= {'ic_trade_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/trade_v1/minute_norm',
                'ic_prod_v6':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_prod_v6/minute_norm',
                'if_prod_v5_add':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v5/minute_norm',
                'ic_short_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_short_v2/minute_norm',
                'if_v6nl':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_prod_v6/minute_norm',
                'ic_v7c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_prod_v7_2/minute_norm',
                'ic_short_v3c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_short_v3/minute_norm',
                'if_v7c':'/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/IF_prod_v7/minute_norm'}

fac_desc_raw_path_dict = {'ic_trade_v1':'',
                          'ic_prod_v6':'',
                          'if_prod_v5_add':'',
                          'ic_short_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear/minute_norm',
                          'if_v6nl':'',
                          'ic_v7c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_diff_zscore/minute_norm',
                          'ic_short_v3c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_diff_zscore/minute_norm',
                          'if_v7c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_diff_zscore/minute_norm'}

fac_desc_norm_path_dict = {'ic_trade_v1':'',
                           'ic_prod_v6':'',
                           'if_prod_v5_add':'',
                           'ic_short_v1':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
                           'if_v6nl':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm',
                           'ic_v7c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
                           'ic_short_v3c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IC_nonlinear_zscore/minute_norm',
                           'if_v7c':'/data/group/800466/warehouse/prod/alpha/CHINA_FUTURES/MINUTE/IF_nonlinear_zscore/minute_norm'}                 

### additional descriptor in format of list of factor path
fac_add_path_dict = {'if_v7c':['/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_zscore/minute_norm/',
                               '/data/group/800466/warehouse/test/alpha/CHINA_FUTURES/MINUTE/if_features_new_181_diff_zscore/minute_norm/']}

comb2_model_list =['mlp_reg','lstm_cla']
model_list_extra = ['rff_cla','rfe_cla']
model_list_onnx = ['crn_cla','crn_reg']
model_list_rnn = ['lstm_cla','lstm_reg','crn_cla','crn_reg']

long_list = [10,20,30]
short_list = [1,5,10] 
hpr_spec_dict_all = {
                    'ic_trade_v1':{i:long_list for i in model_list_dict['ic_trade_v1']},
                    'ic_prod_v6':{i:long_list for i in model_list_dict['ic_prod_v6']},
                    'if_prod_v5_add':{**{i:long_list for i in ['lasso_reg','lr_cla','et_cla','lstm_cla','mlp_reg']},
                                      **{i:short_list for i in ['lgbm_cla']}},
                    'ic_short_v1':{**{i:long_list for i in ['lstm_cla','et_cla']},
                                   **{i:short_list for i in ['rff_cla','rfe_cla','lgbm_cla','lgbm_reg','mlp_reg']}},
                    'if_v6nl':{**{i:long_list for i in ['lstm_cla','et_cla','lr_cla']},
                               **{i:short_list for i in ['lasso_reg','lgbm_cla','lgbm_reg','mlp_reg']}},
                    'ic_v7c':{**{i:long_list for i in ['lstm_cla','et_cla']},
                              **{i:short_list for i in ['lasso_reg','lr_cla','lgbm_cla','lgbm_reg','mlp_reg']}},
                    'ic_short_v3c':{i:short_list for i in model_list_dict['ic_short_v3c']},
                    'if_v7c':{**{i:short_list for i in ['lasso_reg','lgbm_cla','lgbm_reg','mlp_reg','mlp_cla']},
                             **{i:long_list for i in ['lr_cla','et_cla','lstm_cla']}}
                    }    
with_desc_dict = {'ic_trade_v1':False,'ic_prod_v6':False,'if_prod_v5_add':False,'ic_short_v1':True,'if_v6nl':False,'ic_v7c':True,'ic_short_v3c':True,'if_v7c':True} # nonlinear_raw_factor # for cc rfe rff only

with_desc_norm_dict = {'ic_trade_v1':False,'ic_prod_v6':False,'if_prod_v5_add':False,'ic_short_v1':True,'if_v6nl':True,'ic_v7c':True,'ic_short_v3c':True,'if_v7c':True} # nonlinear_factor_norm

time_step_dict = {**{i:30 for i in ['ic_trade_v1','ic_prod_v6','if_prod_v5_add','ic_short_v1']},
                  **{i:10 for i in ['if_v6nl','ic_v7c','ic_short_v3c','if_v7c']}}
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
flag_rootpath = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS_sim/'   
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



def get_current_date(new_date_time=18,print_info=False):
    """if current date is not pass new_date_time such as 18 (6pm)
         it will return previous trading day
    """
    current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    current_date = int(current_time[:8])
    current_hour = int(current_time[9:11])
    print('Current time: ' + str(current_time))
    fdate_list_dt = IO.read_data([20090101, 20300101], ftype=FType.CALENDAR).index.get_level_values(0)
    fdate_list = [int(dt.datetime.strftime(i, '%Y%m%d')) for i in fdate_list_dt]
    nearest_date = min(fdate_list, key=lambda x: abs(x - current_date) if x <= current_date else 100)
    if current_hour < new_date_time and nearest_date == current_date:
        current_date_use = fdate_list[fdate_list.index(current_date) - 1]
        if print_info:
            print('Not till refresh time ' + str(new_date_time) + ':00')        
            print('Use previous trading date: ' + str(current_date_use))
    elif current_hour >= new_date_time and nearest_date == current_date:
        if print_info:
            print('Right on time: ' + str(current_date))
        current_date_use = current_date
    elif nearest_date < current_date:
        current_date_use = nearest_date
    elif nearest_date > current_date:
        current_date_use = fdate_list[fdate_list.index(nearest_date) - 1]
    return current_date_use

def concat_pd_spec(exist_df,update_df,use_update=False,dropna=True, spec=False):
    if spec == True:
        exist_df[(exist_df.index.hour == 9) & (exist_df.index.minute == 30)] = 9999
        update_df[(update_df.index.hour == 9) & (update_df.index.minute == 30)] = 9999  
    if dropna:
        update_df = update_df.dropna()
        exist_df = exist_df.dropna()
    if spec == True:
        exist_df[(exist_df.index.hour == 9) & (exist_df.index.minute == 30)] = np.nan
        update_df[(update_df.index.hour == 9) & (update_df.index.minute == 30)] = np.nan        
    if isinstance(use_update,bool):
        if use_update:
            new_index = update_df.index[0]
            update_df_slice = update_df                 
            exist_df_slice = exist_df.loc[:new_index]
            if new_index in exist_df_slice.index:
                exist_df_slice = exist_df_slice.iloc[:-1]            
        else:
            new_index = exist_df.index[-1]
            exist_df_slice = exist_df
            update_df_slice = update_df.loc[new_index:]
            if new_index in update_df_slice.index:
                update_df_slice = update_df_slice.iloc[1:]            
    else:
        exist_df_slice = exist_df.loc[:use_update]
        new_index = exist_df_slice.index[-1]
        update_df_slice = update_df.loc[new_index:]
    if len(exist_df_slice)>0:    
        sdate_exist,edate_exist = exist_df_slice.index[0],exist_df_slice.index[-1]
    else:
        sdate_exist,edate_exist = '',''
    if len(update_df_slice)>0:
        sdate_update,edate_update = update_df_slice.index[0],update_df_slice.index[-1]
    else:
        sdate_update,edate_update = '',''
    print('ConcatPD: use_update:%s dropna:%s |exists:%s ~ %s | update: %s ~ %s'%(use_update,dropna,sdate_exist,edate_exist,sdate_update,edate_update))
    pred_cat_df = pd.concat([exist_df_slice,update_df_slice],axis=0)
    return pred_cat_df
    
def place_back_format(dat_mat,dat_orig):
    if isinstance(dat_orig,pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat,index=dat_orig.index,columns=dat_orig.columns)
    elif isinstance(dat_orig,pd.Series):
        dat_fmt = pd.Series(dat_mat,index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt

def calc_ts_pct(ts_dat,roll_win=20,min_pct=1,force_range=True):
    min_win = max(int(min_pct*roll_win),1)
    ts_dat_pct_np = bk.move_rank(ts_dat,window=roll_win,min_count=min_win,axis=0)
    if force_range:
        ts_dat_pct_np = (ts_dat_pct_np + 1)/2
    ts_dat_pct = place_back_format(ts_dat_pct_np,ts_dat)
    return ts_dat_pct


def read_pickle(save_path=None,verbose=True):
    tic = time.time()
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    toc = time.time()
    #if verbose:
    #    print('loading done - %s - %s   '%(print_time(toc,tic),save_path))
    return save_dict


def save_pickle(save_dict,save_path):
    print ('saving data to:\n',save_path)
    folder= os.path.dirname(save_path)
    if not os.path.exists(folder):
        try:
            os.makedirs(folder)
        except:
            pass
    if os.path.exists(save_path):
        try:
            print ('remove existing one')
            os.remove(save_path)
        except:
            pass
    with open(save_path, 'wb') as input:
            pickle.dump(save_dict,input,protocol=pickle.HIGHEST_PROTOCOL)
    return 


def find_file(root_path,suffix='h5',file_name_only=False):
    factor_path_dict = {}
    for path, subdirs, files in os.walk(root_path):
        for name in files:
            if suffix in name:
                fac_name = name[:-len(suffix)-1]
                factor_path_dict[fac_name] = os.path.join(path, name)
    if file_name_only:
        factor_path_dict = {fac:os.path.basename(fac).replace('.%s'%(suffix),'') for fac in factor_path_dict}
        factor_path_dict = list(factor_path_dict.values())
    return factor_path_dict

def read_ts_fac_helper(fac_base,xs_name=None):
    fac_path_dict = find_file(fac_base,'h5')
    fac_val_list = []
    fac_name_list = []
    for fac_name in fac_path_dict:
        fac_itr = pd.read_hdf(fac_path_dict[fac_name])
        if xs_name is not None: 
            fac_itr = fac_itr.xs(xs_name,level=1)
        if isinstance(fac_itr,pd.DataFrame):
            if 'norm' in fac_itr.columns:
                fac_itr = fac_itr['norm']
        fac_val_list.append(fac_itr)
        fac_name_list.append(fac_name)
    fac_val = pd.concat(fac_val_list,axis=1)
    fac_val.columns = fac_name_list
    print(fac_val.shape)
    return fac_val


try:  
    import onnx
    import onnxruntime as ort
except:
    print('import onnx error')
    


# pred_template for onnx model
def pred_template_onnx(x, model):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    ort_sess = ort.InferenceSession(model)
    ys = []
    for t in range(x_np.shape[0]):
        xt = x_np[t:t + 1]
        res = ort_sess.run(None, {ort_sess.get_inputs()[0].name: xt.astype(np.float32)})
        ys.append(res[0])
    y_np = np.concatenate(ys, axis=0)
    return y_np

def change_h5_path_helper(model_fold_itr,res_base_path):
    file_name = os.path.basename(model_fold_itr)
    dest_root = res_base_path.split('.')[0]
    model_fold_itr = os.path.join(dest_root,file_name)
    return model_fold_itr


# fixd on 20221220 ~ 1. support onnx format 2. support address change for h5/onnx if pass in res_base_path
def pred_helper(x_test,model_dict,pred='regression',check_time=True,return_itr=False):
    # accept lstm with time_step  / keras model ~ mlp
    sdt_pred = x_test.index[0]
    ts_list = list(model_dict['model'].keys())
    ts_list.sort()
    ts_take = ts_list[-1]
    if check_time:
        if sdt_pred<ts_take:
            print('Raise Error: modeled trained in future time')
            print('model: %s / pred: %s'%(str(ts_take),str(sdt_pred)))
            raise Exception

    model_fold = model_dict['model'][ts_take]
    if 'feature_importance' in model_dict:
        fi_fold = model_dict['feature_importance'][ts_take]
    else:
        fi_fold = x_test.columns.tolist()
    pred_shape = x_test.shape[0]
    fold_list = list(model_fold.keys())
    fold_num = len(fold_list)
    print('use model trained on %s with %d fold'%(ts_take,fold_num))    
    pred_res_itr_list = []
    for fold_itr in fold_list:
        fi_fold_itr = fi_fold[fold_itr]
        fi_fold_itr_list = fi_fold_itr.index.tolist()
        x_test_fold = x_test[fi_fold_itr_list]
        model_fold_itr = model_fold[fold_itr]
        if isinstance(model_fold_itr,str):
            model_fold_itr = load_model(model_fold_itr)   
            model_config = model_fold_itr.get_config()[0]
            if model_config['class_name'] == 'LSTM': # solve for lstm 3d data, pred return np.array
                time_step = model_config['config']['batch_input_shape'][1]
                pred_idx = len(x_test_fold) - time_step + 1
                pred_index = x_test_fold.iloc[-pred_idx:].index
                pred_shape = len(pred_index)
                x_test_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
        pred_res_itr = pred_template(x=x_test_fold,model = model_fold_itr,pred=pred)
        if isinstance(pred_res_itr,np.ndarray):
            pred_res_itr = pd.Series(pred_res_itr.flatten(), index=pred_index)
        pred_res_itr_list.append(pred_res_itr)
    print('pred shape: %d'%(pred_shape)) 
    pred_res_itr_df = pd.concat(pred_res_itr_list,axis=1)
    pred_res_itr_df.columns = fold_list
    pred_res = pred_res_itr_df.mean(axis=1)
    if return_itr:
        return pred_res,pred_res_itr_df
    else:
        return pred_res   
"""
def pred_helper(x_test,model_dict,pred='regression',check_time=True,return_itr=False):
    # accept lstm with time_step  / keras model ~ mlp
    sdt_pred = x_test.index[0]
    ts_list = list(model_dict['model'].keys())
    ts_list.sort()
    ts_take = ts_list[-1]
    if check_time:
        if sdt_pred<ts_take:
            print('Raise Error: modeled trained in future time')
            print('model: %s / pred: %s'%(str(ts_take),str(sdt_pred)))
            raise Exception

    model_fold = model_dict['model'][ts_take]
    if 'feature_importance' in model_dict:
        fi_fold = model_dict['feature_importance'][ts_take]
    else:
        fi_fold = x_test.columns.tolist()
    pred_shape = x_test.shape[0]
    fold_list = list(model_fold.keys())
    fold_num = len(fold_list)
    print('use model trained on %s with %d fold'%(ts_take,fold_num))    
    pred_res_itr_list = []
    for fold_itr in fold_list:
        fi_fold_itr = fi_fold[fold_itr]
        fi_fold_itr_list = fi_fold_itr.index.tolist()
        x_test_fold = x_test[fi_fold_itr_list]
        model_fold_itr = model_fold[fold_itr]
        if isinstance(model_fold_itr,str):
            model_fold_itr = load_model(model_fold_itr)   
            model_config = model_fold_itr.get_config()[0]
            if model_config['class_name'] == 'LSTM': # solve for lstm 3d data, pred return np.array
                time_step = model_config['config']['batch_input_shape'][1]
                pred_idx = len(x_test_fold) - time_step + 1
                pred_index = x_test_fold.iloc[-pred_idx:].index
                pred_shape = len(pred_index)
                x_test_fold = transform_2d_3d_helpher(x_test_fold.values, None, time_step)
        pred_res_itr = pred_template(x=x_test_fold,model = model_fold_itr,pred=pred)
        if isinstance(pred_res_itr,np.ndarray):
            pred_res_itr = pd.Series(pred_res_itr.flatten(), index=pred_index)
        pred_res_itr_list.append(pred_res_itr)
    print('pred shape: %d'%(pred_shape)) 
    pred_res_itr_df = pd.concat(pred_res_itr_list,axis=1)
    pred_res_itr_df.columns = fold_list
    pred_res = pred_res_itr_df.mean(axis=1)
    if return_itr:
        return pred_res,pred_res_itr_df
    else:
        return pred_res
"""

def pred_template(x,model,pred='regression',best_iteration=False):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    if pred=='regression':
    #if 'predict' in model_fold_itr.__dir__():
        y_mat = model.predict(x_np)
    else:
        if len(x_np.shape)>2:
            y_mat = model.predict_proba(x_np).flatten()
        else:
            if best_iteration:
                y_mat = model.predict_proba(x_np,ntree_limit=model.best_iteration)[:, 1]
            else:
                y_mat_temp = model.predict_proba(x_np)
                if np.shape(y_mat_temp)[1] > 2:
                    y_mat = y_mat_temp[:, -1] - y_mat_temp[:, 0]
                else:
                    y_mat = y_mat_temp[:, 1]
    
    if x_type == 'pd':
        y = pd.Series(y_mat.flatten(),index=x.index)
    else:
        y = y_mat
    return y    


####20211201##### add mlp/lstm prediction fucntion
# support slice data by time_step 
def process_dat_wrapper_inner(x_train,x_test=None,x_val=None,process_func=StandardScaler()):
    """
    process_func: MinMaxScaler / StandardScaler / QuantileTransformer
    """
    scaler = process_func
    scaler.fit(x_train)
    #print(scaler.mean_)
    x_train_norm_np = scaler.transform(x_train)
    x_train_norm = place_back_format(x_train_norm_np,x_train)
    res_dict = {}
    res_dict['train'] = x_train_norm
    res_dict['scaler'] = scaler
    if x_test is not None:
        x_test_norm_np = scaler.transform(x_test)
        x_test_norm = place_back_format(x_test_norm_np,x_test)
        res_dict['test'] = x_test_norm
    if x_val is not None:
        x_val_norm_np = scaler.transform(x_val)
        x_val_norm = place_back_format(x_val_norm_np,x_val)
        res_dict['val'] = x_val_norm
    return res_dict


def process_dat_wrapper(x_train,x_test=None,x_val=None,process_func=StandardScaler(),process_col_list=None):
    col_list = x_train.columns.tolist()
    if process_col_list is None:
        res_dict = process_dat_wrapper_inner(x_train=x_train,x_test=x_test,x_val=x_val,process_func=StandardScaler())
    else:
        left_col_list = [i for i in x_train.columns if i not in process_col_list]
        x_train_process = x_train[process_col_list]
        x_train_left = x_train[left_col_list]
        if x_test is None:
            x_test_process = None  
        else:
            x_test_process = x_test[process_col_list]
            x_test_left = x_test[left_col_list]
        if x_val is None:
            x_val_process = None  
        else:
            x_val_process = x_val[process_col_list]
            x_val_left = x_val[left_col_list]
        rdp = process_dat_wrapper_inner(x_train=x_train_process,
                            x_test=x_test_process,
                            x_val=x_val_process,process_func=process_func)
        res_dict = {}
        res_dict['train'] = pd.concat([rdp['train'],x_train_left],axis=1)
        res_dict['train'] = res_dict['train'][col_list]
        if x_test is None:
            res_dict['test'] = None
        else:
            res_dict['test'] = pd.concat([rdp['test'],x_test_left],axis=1)
            res_dict['test'] = res_dict['test'][col_list]
        if x_val is None:
            res_dict['val'] = None
        else:
            res_dict['val'] = pd.concat([rdp['val'],x_val_left],axis=1)
            res_dict['val'] = res_dict['val'][col_list]
    return res_dict

def prep_train_test_helper(x,sdate_pred,time_step=None,train_s='2016',process_list=None):
    # if time_step consider, it's okay to use full train with overalp to get scaler
    x_train = x.loc[train_s:sdate_pred]
    x_test = x.loc[sdate_pred:]    
    if time_step is not None:
        x_dt_list = x.index.tolist()
        sdate_pred_dt = x_test.index[0]
        sdate_pred_ts_idx = x_dt_list.index(sdate_pred_dt) - time_step + 1
        #x_train = x.iloc[:sdate_pred_ts_idx]
        x_test = x.iloc[sdate_pred_ts_idx:]
    if process_list == 'x':
        process_dat_func = partial(process_dat_wrapper,
                                   process_func=StandardScaler(),
                                   process_col_list=None)
        scaler_dict = process_dat_func(x_train.fillna(0),x_test.fillna(0))
        x_train,x_test = scaler_dict['train'],scaler_dict['test']
    return x_train,x_test

def transform_2d_3d_helpher(x_use,y_use=None,time_step=1):
    x_len = len(x_use)
    if x_len<time_step:
        print ('x length shorter than time step')
        raise Exception
    # reshape input to be [samples, time steps, features]
    if time_step==1:
        x_use_3d = x_use.reshape((x_use.shape[0],1,x_use.shape[1]))
        y_use_3d = y_use
    else:
        x_use_3d = []
        for i in range(x_len-time_step+1):
            x_sequence = x_use[i:i+time_step, :]
            x_use_3d.append(x_sequence)
        x_use_3d = np.array(x_use_3d)
    if y_use is None:
        return x_use_3d
    else:
        y_use_3d = y_use[time_step-1:]
    return x_use_3d,y_use_3d

from keras.backend.tensorflow_backend import set_session
from keras.backend.tensorflow_backend import clear_session
from keras.backend.tensorflow_backend import get_session
from tensorflow.python.platform import gfile

import tensorflow as tf
from tensorflow.python.framework import graph_util
from tensorflow.python.framework import graph_io

def reset_keras(model=None,hist=None):
    sess = get_session()
    clear_session()
    sess.close()
    sess = get_session()
    if model is not None:
        try:
            del model # this is from global space - change this as you need
            if hist is not None:
                del hist
        except:
            pass
    for i in range(3): gc.collect()
    config = tf.ConfigProto()
    config.gpu_options.per_process_gpu_memory_fraction = 1
    config.gpu_options.visible_device_list = "0"
    set_session(tf.Session(config=config))
    return 

from keras.models import model_from_yaml
# fixed i 20211215 to support recreate model in tf 1.4.0
def h5_to_pb_helper(h5_path,pb_path,rebuild=True,tf_version='1.4.0'):
    reset_keras()
    if str(Path(pb_path).parent) == '.':
        pb_path = str((Path.cwd() / pb_path))
    output_fld = Path(pb_path).parent
    output_model_name = Path(pb_path).name
    output_model_stem = Path(pb_path).stem
    input_output_info_txt = os.path.join(output_fld,output_model_stem + '.txt')
    Path(pb_path).parent.mkdir(parents=True, exist_ok=True)
    K.set_image_data_format('channels_last')
    if isinstance(h5_path,str):
        model = load_model(h5_path)
    else:
        model = h5_path
    if rebuild:
        # get structure & weight ~ rebuild from current environment save as pb
        tf_version_curr = tf.__version__
        if tf_version_curr != tf_version:
            print('version error')
            print('tf version current vs required:%s vs %s'%(tf_version_curr,tf_version))
            raise Exception
        weight_path = 'tmp_weight.h5'
        structure_path = 'tmp_structure.yaml'
        model.save_weights(weight_path)
        yaml_string = model.to_yaml()
        open(structure_path, 'w').write(yaml_string) 
        reset_keras(model)
        model = model_from_yaml(yaml_string) # load structure
        model.load_weights(weight_path) # load weight 
    input_name = model.inputs[0].name
    output_name = model.outputs[0].name
    output_name_list = [node.op.name for node in model.outputs]
    with open(input_output_info_txt, 'w+') as f:
        f.write(input_name+',') 
        f.write(output_name)
    sess = K.get_session()
    constant_graph = graph_util.convert_variables_to_constants(
        sess,
        sess.graph.as_graph_def(),
        output_name_list)
    graph_io.write_graph(constant_graph, str(output_fld), output_model_name,
                         as_text=False)
    reset_keras()
    return

def read_pb_model_helper(pb_path):
    reset_keras()
    if str(Path(pb_path).parent) == '.':
        pb_path = str((Path.cwd() / pb_path))
    output_fld = Path(pb_path).parent
    output_model_name = Path(pb_path).name
    output_model_stem = Path(pb_path).stem
    input_output_info_txt = os.path.join(output_fld,output_model_stem + '.txt')
    with open(input_output_info_txt, 'r') as f:
        input_name,output_name = f.readline().split(',')  
    sess = tf.Session()
    with gfile.FastGFile(pb_path,'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        tf.import_graph_def(graph_def,name='')        
    sess.run(tf.global_variables_initializer())        
    input_data = sess.graph.get_tensor_by_name(input_name)
    prediction = sess.graph.get_tensor_by_name(output_name)
    pb_obj = {'sess':sess,'input_data':input_data,'prediction':prediction}
    return pb_obj

"""
def pred_helper_pb_model(pb_obj,x_test):
    sess = pb_obj['sess']
    prediction = pb_obj['prediction']
    input_data = pb_obj['input_data']
    if 'lstm' in pb_obj['input_data'].name:
        time_step = pb_obj['input_data'].shape[1].value
        x_test_use = transform_2d_3d_helpher(x_test.values, None, time_step)
        pred_idx = len(x_test) - time_step + 1
        pred_index = x_test.iloc[-pred_idx:].index
    else:
        x_test_use = x_test
        pred_index = x_test.index
    pred_raw_np = sess.run(prediction,{input_data:x_test_use})
    pred_raw = pd.Series(pred_raw_np.flatten(),index=pred_index)
    return pred_raw
"""
### fixed on 20221220 ~ 
def pred_helper_pb_model(pb_obj,x_test):
    sess = pb_obj['sess']
    prediction = pb_obj['prediction']
    input_data = pb_obj['input_data']
    if 'feature_importance' in pb_obj:
        x_test = x_test[pb_obj['feature_importance']]
    if 'lstm' in pb_obj['input_data'].name:
        time_step = pb_obj['input_data'].shape[1].value
        print(time_step)
        x_test_use = transform_2d_3d_helpher(x_test.values, None, time_step)
        pred_idx = len(x_test) - time_step + 1
        pred_index = x_test.iloc[-pred_idx:].index
    else:
        x_test_use = x_test
        pred_index = x_test.index
    pred_raw_np = sess.run(prediction,{input_data:x_test_use})
    if len(pred_raw_np.shape)>1:
        if pred_raw_np.shape[1]==2:
            pred_raw_np = pred_raw_np[:,1]
    pred_raw = pd.Series(pred_raw_np.flatten(),index=pred_index)
    return pred_raw


def minute_flag_check(date):
    path1 = flag_rootpath + str(date) + '/' + 'if_factors.success' 
    path2 = flag_rootpath + str(date) + '/' + 'ih_factors.success' 
    path3 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_ic_zscore.success'
    path4 = '/data/group/800466/warehouse/prod/MD/MarketData/LOCAL_DATA/FLAGS/' + str(date) + '/' + str(date) + '_if_zscore.success'
    return os.path.exists(path1) and os.path.exists(path2) and os.path.exists(path3) and os.path.exists(path4)


def slice_by_minute(dat, slice_range=[1000, 1454]):
    """ minute mark at the start
         use left close, right open  - except 1500 - include that
         slice_range = [[1125,1129],[1300,1310]]

    """
    if isinstance(dat.index,pd.MultiIndex):
        index_list = dat.index.get_level_values(0)
    else:
        index_list = dat.index
    hour_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.hour]
    minute_list = ['%s' % (i) if i > 9 else '0%s' % (i) for i in index_list.minute]
    hour_minute_list = [int('%s%s' % (i, j)) for i, j in zip(hour_list, minute_list)]
    if isinstance(slice_range[0],list):
        range_a = slice_range[0]
        range_b = slice_range[1]
        range_a.sort()
        range_b.sort()
        slice_mask = [(i <= range_a[-1] and i >= range_a[0]) or
                      (i <= range_b[-1] and i >= range_b[0])
                      for i in hour_minute_list]
    else:
        slice_range.sort()
        slice_mask = [i <= slice_range[-1] and i >= slice_range[0] for i in hour_minute_list]
    dat_slice = dat[slice_mask]
    return dat_slice

################## 
# 股指分钟模型合成部分 ~ 20210909 / zsj
# 模型合成部分：　
#１.　拼接最新预测值与过去的预测值
# ２. 针对每个模型，每个持仓周期预测原始值进行标准化
# ３. 将所有标准化后的模型预测，5个模型分别3个预测周期，总共15个预测值进行平均，再做一次标准化得到pred_comb为最终结果

# raw_dict: 模型预测原始值，{'lasso_reg':pd.DataFrame}
# raw_dict_update： 根据model.predict 实时生成的模型预测值
# raw_dict_exist： 过去的模型预测原始值
# raw_path_dict_prev： 过去的原始预测值路径

# date
#edate = '20220207'
# edate = str(get_current_date())#get_next_date() # note



for edate in date_list:
    edate = str(edate)
    print(edate)
    print('------wait data flag')
    while True:
        if minute_flag_check(edate):
            break
        time.sleep(60)
    print('flag check finished!')
    flag_path = flag_rootpath + str(edate) + '/'
    os.makedirs(flag_path,exist_ok=True)
    flag_path_start = flag_path + str(edate) + '_model.start'
    with open(flag_path_start,'w') as file:
        pass 
    for version in version_list:
        print(version)
        ticker = version_ticker_dict[version]
        model_date = model_date_dict[version]
        model_date_use = model_date_use_dict[version]
        ts_pct_win = ts_pct_win_dict[version]
        ts_pct_win2 = ts_pct_win_dict2[version]
        model_list = model_list_dict[version] 
        hpr_spec_dict = hpr_spec_dict_all[version] 
        fac_path = fac_path_dict[version]
        fac_desc_path = fac_desc_raw_path_dict[version]
        fac_desc_norm_path = fac_desc_norm_path_dict[version]
        with_desc = with_desc_dict[version]
        with_desc_norm = with_desc_norm_dict[version]
        comb1_list = list(set(model_list) - set(comb2_model_list))
        comb2_list = list(set(comb1_list + comb2_model_list))
        time_step = time_step_dict[version]
        # path 

        model_root = os.path.join(dat_root,'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_file/' % str(model_date_use))
        pred_raw_root = os.path.join(dat_root,'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw'% str(model_date_use))
        pred_raw_itr_root = os.path.join(dat_root,'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_raw_itr'% str(model_date_use))
        pred_norm_root = os.path.join(dat_root,'alpha/CHINA_FUTURES/MINUTE/model/model_update/%s/model_value/model_norm'% str(model_date_use))

        #############
        # create path 
        fac_root = os.path.join(dat_root,'alpha/CHINA_FUTURES/MINUTE')
        flag_root = os.path.join(dat_root,'MD/MarketData/LOCAL_DATA/FLAGS')
        dummy_path = os.path.join(fac_root,'dummies/minute_norm')
        #flag_path_dict = {i:os.path.join(flag_root,edate,'%s_%s_factors.success'%(edate,i)) for i in init_list}

        ##############
        # 0. check data flag & load factor data
        """
        for i in flag_path_dict:
            if not os.path.exists(flag_path_dict[i]):
                print('failed')
                raise Exception
            else:
                print('flag check:  %s %s  ~ success'%(edate,i))
        """
        print('reading factors')
        dummy = read_ts_fac_helper(dummy_path)
        fac = read_ts_fac_helper(fac_path)
        dummy2 = dummy.copy()
        dummy2.columns = [i+'.0' for i in dummy.columns]
        dummy_use = pd.concat([dummy,dummy2],axis=1)
        fac_val_list = []
        fac_val_list.append(fac)
        if with_desc:
            fac_desc = read_ts_fac_helper(fac_desc_path)
            fac_val_list.append(fac_desc)
        if with_desc_norm:
            fac_desc_norm = read_ts_fac_helper(fac_desc_norm_path)
            fac_val_list.append(fac_desc_norm)
        fac_val_list.append(dummy_use)
        if version in fac_add_path_dict:
            print('fac add path: %s ~ \n%s'%(version,str(fac_add_path_dict[version])))
            for path_itr in fac_add_path_dict[version]:
                fac_itr = read_ts_fac_helper(path_itr)
                fac_val_list.append(fac_itr)
        x_test = pd.concat(fac_val_list,axis=1).loc[:edate].fillna(0)
        #x_test = pd.concat([fac,fac_desc,fac_desc_norm,dummy_use],axis=1).loc[:edate].fillna(0)

        dt_list = list(set(x_test.index.date))
        dt_list = [dt.datetime.strftime(i,'%Y%m%d') for i in dt_list]
        dt_list.sort()
        #edate_prev = '20210923'
        edate_prev = dt_list[dt_list.index(edate) - 1]
        print('prep factor done')

        sdate_pred = edate
        x_train,x_test_itr = prep_train_test_helper(x_test,sdate_pred,time_step=None,
                                                train_s=train_s,process_list=process_list)                                            
        x_train_ts,x_test_itr_ts = prep_train_test_helper(x_test,sdate_pred,time_step=time_step,
                                                train_s=train_s,process_list=process_list)

        model_list = list(hpr_spec_dict.keys())
        raw_path_dict_prev = {model:os.path.join(pred_raw_root,str(edate_prev),'%s.pkl'%(model)) for model in model_list}
        raw_path_dict = {model:os.path.join(pred_raw_root,edate,'%s.pkl'%(model)) for model in model_list}
        norm_path_dict = {model:os.path.join(pred_norm_root,edate,'%s.pkl'%(model)) for model in model_list}
        raw_dict_update = {}
        #for model in model_list:
        #roll_name = '_r720'
        roll_name = roll_name_dict[version]
        def mmodel(model):
            holding_period_list = hpr_spec_dict[model]
            raw_list = []
            for holding_period in holding_period_list:
                print(model,holding_period)
                #pa_path = os.path.join(model_root,model,'%s_%d_r240.pkl'%(model,holding_period))
                pa_path = os.path.join(model_root,model,'%s_%d%s.pkl'%(model,holding_period,roll_name))   # roll_name = '_r720'             
                model_dict = read_pickle(pa_path)
                #pa_path2 = os.path.join(model_root2,model,'%s_%d_r240.pkl'%(model,holding_period))
                #save_pickle(model_dict,pa_path2)
                raw_itr_path = os.path.join(pred_raw_itr_root,edate,'%s_%d.pkl'%(model,holding_period))
                pred = 'regression' if model.find('reg')>=0 else 'classification'
                if model in model_list_rnn:
                    x_test_input = x_test_itr_ts
                else:
                    x_test_input = x_test_itr
                pred_raw_itr,pred_res_itr_df = pred_helper(x_test_input,model_dict,pred=pred,check_time=check_time,
                                                               return_itr=return_itr)

                #pred_raw_itr,pred_res_itr_df = pred_helper(x_test_itr,model_dict,pred=pred,check_time=check_time,return_itr=return_itr)  
                raw_list.append(pred_raw_itr)
                save_pickle(pred_res_itr_df,raw_itr_path)
            raw_df_itr = pd.concat(raw_list,axis=1)
            raw_df_itr.columns = ['%s_%d'%(model,i) for i in holding_period_list]
            raw_dict_update[model] = raw_df_itr
            return [model, raw_df_itr]
        with Pool(24) as pool:
            raw_dict_update1 = pool.map(mmodel, model_list)
        for item in raw_dict_update1:
            raw_dict_update[item[0]] = item[1]
        
        #     save_pickle(raw_df_itr,raw_path_dict_prev[model])
        print('model update generated')

        print('model combine') 
        ###################
        #１.　拼接最新预测值与过去的预测值
        raw_dict_exist = {}
        raw_dict = {}
        raw_dict_exist_last = {}

        # 每个模型的名字列表 比如 lasso_reg_10 (laso_reg针对10分钟的预测)
        model_name_dict = {model:['%s_%d'%(model,h) for h in hpr_spec_dict[model]] for model in model_list}
        print('1. append prediction')
        for model in model_list:
            print(model)
            raw_dict_exist[model] = read_pickle(raw_path_dict_prev[model])
            name_list_itr = model_name_dict[model]
            raw_dict_exist[model] = raw_dict_exist[model][name_list_itr]
            raw_dict_update[model] = raw_dict_update[model][name_list_itr]
            if model in model_list_extra:
                raw_dict[model] = concat_pd_spec(raw_dict_exist[model],raw_dict_update[model],use_update=use_update,dropna=dropna, spec = True)
            else:
                raw_dict[model] = concat_pd_spec(raw_dict_exist[model],raw_dict_update[model],use_update=use_update,dropna=dropna)
            save_pickle(raw_dict[model],raw_path_dict[model])

        # ２. 针对每个模型，每个持仓周期预测原始值进行标准化
        print ('2. getting normlized prediction for sub model')
        pred_norm_dict = {}
        for model in model_list:
            print('*'*30)
            print(model)
            pred_df = raw_dict[model]
            take_list = pred_df.columns
            if model in model_list_extra:
                print('note: slice %s by %s'%(model,str(slice_range_extra)))
                dt_list_orig = pred_df.index.tolist()
                pred_df = slice_by_minute(pred_df,slice_range_extra).reindex(index=dt_list_orig)
            pred_norm = {}
            for factor_name in take_list:
                print(factor_name)
                pred_norm[factor_name] = calc_ts_pct(pred_df[factor_name],ts_pct_win,min_pct=min_pct)
                pred_norm_df = pd.DataFrame(pred_norm)
                pred_norm_df.index.name = 'dt'
            pred_norm_dict[model] = pred_norm_df
            print('*'*30)

        # ３. 将所有标准化后的模型预测，5个模型分别3个预测周期，总共15个预测值进行平均，再做一次标准化得到pred_comb为最终结果
        print('3. stack all prediction')
        pred_hpr_raw_list = []
        for model in model_list:
            print(model)
            factor_name = model
            use_list_spec = ['%s_%d'%(model,h) for h in hpr_spec_dict[model]]
            hpr_raw = pred_norm_dict[model][use_list_spec].mean(axis=1)
            hpr_raw = pd.DataFrame(hpr_raw,columns = [model])
            pred_hpr_raw_list.append(hpr_raw)
            save_pickle(hpr_raw,norm_path_dict[model])

        pred_hpr_raw = pd.concat(pred_hpr_raw_list,axis=1)

        factor_name = 'pred_comb'
        norm_path_dict[factor_name] =os.path.join(pred_norm_root,edate,'%s.pkl'%(factor_name))
        pred_comb_raw = pred_hpr_raw[comb1_list].mean(axis=1)
        pred_comb = calc_ts_pct(pred_comb_raw,ts_pct_win2,min_pct=min_pct)
        save_pickle(pred_comb,norm_path_dict[factor_name])

        factor_name = 'pred_comb2'
        norm_path_dict[factor_name] =os.path.join(pred_norm_root,edate,'%s.pkl'%(factor_name))
        pred_comb_raw2 = pred_hpr_raw[comb2_list].mean(axis=1)
        pred_comb2 = calc_ts_pct(pred_comb_raw2,ts_pct_win2,min_pct=min_pct)
        save_pickle(pred_comb2,norm_path_dict[factor_name])
    flag_path = flag_rootpath + str(edate) + '/'
    flag_path_success = flag_path + str(edate) + '_model.success'
    with open(flag_path_success,'w') as file:
        pass 

lm = link.LinkMessage()
lm.sendMessage('PROD - UPDATE MODEL FINISHED!')
del lm

