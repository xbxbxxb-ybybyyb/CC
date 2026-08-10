
# coding: utf-8

# In[1]:


import numpy as np
import pandas as pd
import os
import datetime
import importlib
import multiprocessing
import sys

import inspect,time,pickle
from keras.models import load_model

################生成因子################
sys.path.insert(0, './factors/factor_list/')

univ = pd.read_pickle('./universe/stock_universe.pkl').reset_index()
for i in univ.values:
	try:
		data = pd.read_csv('./data/Stock/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
		data = data.loc[data.dt < str(i[0] + datetime.timedelta(hours = 9, minutes = 26))].iloc[-1]
		preclose = data.PreClosePx
		
		data = pd.read_csv('./data/Transaction/' + i[1] + '/' + i[0].strftime('%Y%m%d') + '.csv')
		data = data.loc[(data.dt < str(i[0] + datetime.timedelta(hours = 9, minutes = 26))) & (data.TradePrice > 0)].iloc[-1]
		lastpx = data.TradePrice
		if lastpx >= preclose:
			univ.drop(univ.index[univ.Ticker == i[1]], inplace = True)
	except:
		univ.drop(univ.index[univ.Ticker == i[1]], inplace = True)

univ = univ.set_index(['dt', 'Ticker'])
univ.to_pickle('./universe/stock_universe_filtered.pkl')


def calc(i):
    importlib.import_module(i)

pool = multiprocessing.Pool(processes = 24)

factors = [x[:-3] for x in os.listdir('./factors/factor_list/') if x.endswith('.py')]

for i in factors:
    pool.apply_async(calc, (i, ))
    
pool.close()
pool.join()
########################################



################标准化，生成输出################
factor_list = os.listdir('./factors/factor_raw/')
factor_raw = []
for f in factor_list:
    factor_raw.append(pd.read_pickle('./factors/factor_raw/' + f))
factor_raw = pd.concat(factor_raw, axis = 1)
factor_new = pd.read_pickle('./factors/factor_new.pkl')
factor_hist = pd.read_pickle('./factors/factor_hist.pkl')
# factor_sign = pd.read_pickle('./factors/factor_sign.pkl')
factor_dummy = pd.read_pickle('./factors/factor_dummy.pkl')

factor_new = factor_new.reindex(univ.index)
factor_dummy = factor_dummy.reindex(univ.index)

factor_df = pd.concat([factor_hist, pd.concat([factor_raw, factor_new], axis = 1)], sort = True)
# factor_df = factor_df * factor_sign

today = pd.Timestamp(np.unique(factor_df.reset_index(0).dt)[-1]).strftime('%Y%m%d')

def rolling_norm(df):
    df = df.replace([-np.inf, np.inf], np.nan)
    for col in df:
        ub = df[col].mean() + 3*df[col].std()
        lb = df[col].mean() - 3*df[col].std()
        df.loc[df[col] > ub, col] = ub
        df.loc[df[col] < lb, col] = lb

    result = ((df - df.mean()) / df.std()).loc[today:]
    return result
    
def norm_zd(df):
    df = df.replace([-np.inf, np.inf], np.nan)
    df = df.loc[today:]
    for col in df:
        ub = df[col].mean() + 3*df[col].std()
        lb = df[col].mean() - 3*df[col].std()
        df.loc[df[col] > ub, col] = ub
        df.loc[df[col] < lb, col] = lb
        
    result = (df - df.mean()) / df.std()
    result.columns += '_zd' 
    return result
    
factor_input = pd.concat([rolling_norm(factor_df), norm_zd(factor_df), factor_dummy], axis = 1).fillna(0)

factor_input.to_pickle('./factors/factor_input.pkl')
##############################################



################################################模型预测############################################################################

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
            os.makedirs(folder)
    if os.path.exists(save_path):
            print ('remove existing one')
            os.remove(save_path)
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

def change_h5_path_helper(model_fold_itr,res_base_path):
    file_name = os.path.basename(model_fold_itr)
    dest_root = res_base_path.split('.')[0]
    model_fold_itr = os.path.join(dest_root,file_name)
    return model_fold_itr

def pred_helper(x_test,model_dict,pred='regression',check_time=True,return_itr=False,res_base_path=None):
    # accept lstm with time_step  / keras model ~ mlp
    if isinstance(x_test.index,pd.MultiIndex):
        sdt_pred = x_test.index[0][0]
    else:
        sdt_pred = x_test.index[0]
    ts_list = list(model_dict['model'].keys())
    ts_take = ts_list[-1]
    if check_time:
        if sdt_pred<ts_take:
#             print('Raise Error: modeled trained in future time')
#             print('model: %s / pred: %s'%(str(ts_take),str(sdt_pred)))
            raise Exception

    model_fold = model_dict['model'][ts_take]
    if 'feature_importance' in model_dict:
        fi_fold = model_dict['feature_importance'][ts_take]
    else:
        fi_fold = x_test.columns.tolist()
    pred_shape = x_test.shape[0]
    fold_list = list(model_fold.keys())
    fold_num = len(fold_list)
#     print('use model trained on %s with %d fold'%(ts_take,fold_num))    
    pred_res_itr_list = []
    for fold_itr in fold_list:
        fi_fold_itr = fi_fold[fold_itr]
        fi_fold_itr_list = fi_fold_itr.index.tolist()
        x_test_fold = x_test[fi_fold_itr_list]
        model_fold_itr = model_fold[fold_itr]
        if isinstance(model_fold_itr,str):
            if res_base_path is not None:
                model_fold_itr = change_h5_path_helper(model_fold_itr,res_base_path)
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
#     print('pred shape: %d'%(pred_shape)) 
    pred_res_itr_df = pd.concat(pred_res_itr_list,axis=1)
    pred_res_itr_df.columns = fold_list
    pred_res = pred_res_itr_df.mean(axis=1)
    if return_itr:
        return pred_res,pred_res_itr_df
    else:
        return pred_res
    
def pred_template(x,model,pred='regression',best_iteration=False):
    if isinstance(x, pd.DataFrame) or isinstance(x, pd.Series):
        x_type = 'pd'
        x_np = x.values
    else:
        x_type = 'np'
        x_np = x
    if pred=='regression':
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

def get_model_pred_helper(res_base_path, model_name=None):
    if isinstance(res_base_path,dict):
        model_base_dict = res_base_path
    else:
        if res_base_path.find('pkl')>0:
            model_base_dict = {os.path.basename(res_base_path).split('.')[0]:res_base_path}
        else:
            model_base_dict = find_file(res_base_path, 'pkl')
    if model_name is not None:
        if isinstance(model_name,str):
            model_base_dict = {i: model_base_dict[i] for i in model_base_dict
                               if i.find(model_name) >= 0}
        elif isinstance(model_name,list):
            model_base_dict = {i: model_base_dict[i] for i in model_base_dict
                               if i in model_name}
    model_dict = {i: read_pickle(model_base_dict[i]) for i in model_base_dict}
    pred_df = extract_model_pred(model_dict)
    return pred_df, model_dict

def pred_helper_wrapper(x_test, res_base_path, pred='regression', model_name=None,chg_name=False):
    pred_df, model_dict_itr = get_model_pred_helper(res_base_path, model_name)
    if isinstance(x_test.index,pd.MultiIndex):
        date_list_pred = x_test.index.get_level_values(level=0).unique().tolist()
        date_list_exist = pred_df.index.get_level_values(level=0).unique().tolist()
    else:
        date_list_pred = x_test.index.tolist()
        date_list_exist = pred_df.index.tolist()
    date_list_pred.sort()
    date_list_exist.sort()
    last_exist = date_list_exist[-1]
    if last_exist in date_list_pred:
        last_exist_idx = date_list_pred.index(last_exist)
        if last_exist_idx<len(date_list_pred)-1:
            sdate_pred = date_list_pred[last_exist_idx+1]
            pred_task = True
        else:
            pred_task = False
            print('no need for prediction')
    else:
        pred_task = True
        sdate_pred = date_list_pred[0]
    if pred_task:
        x_test_use = x_test.loc[sdate_pred:]
        pred_raw_list = []
        for k in model_dict_itr:
#             print(k)
            pred = 'classification' if k.find('_cla')>0 else 'regression'
            pred_raw_itr = pred_helper(x_test_use, model_dict_itr[k], pred=pred,res_base_path=res_base_path)
            pred_raw_list.append(pred_raw_itr)
        pred_raw_df = pd.concat(pred_raw_list, axis=1)
        pred_raw_df.columns = list(model_dict_itr.keys())
        pred_df_all = pd.concat([pred_df, pred_raw_df], axis=0)
    else:
        pred_df_all = pred_df
    if chg_name:
        pred_df_all.columns = [int(i.split('_')[2]) for i in pred_df_all.columns]        
    return pred_df_all

def extract_model_pred(model_dict):
    model_list = list(model_dict.keys())
    model_list.sort()
    pred_list = []
#     print(model_list)
    for model in model_list:
        model_pred = model_dict[model]['prediction']
        if isinstance(model_pred, pd.DataFrame):
            if model_pred.shape[1] > 1:
                model_pred = model_pred.stack()
        pred_list.append(model_pred)
    pred_df = pd.concat(pred_list, axis=1)
    pred_df.columns = model_list
    return pred_df

def pred_one_helper(x_test, res_base_path, pred='regression', model_name=None,chg_name=False):
    pred_df, model_dict_itr = get_model_pred_helper(res_base_path, model_name)
    pred_raw_list = []
    for k in model_dict_itr:
        pred = 'classification' if k.find('_cla')>0 else 'regression'
        pred_raw_itr = pred_helper(x_test, model_dict_itr[k], pred=pred)
        pred_raw_list.append(pred_raw_itr)
    pred_df_all = pd.concat(pred_raw_list, axis=1)
    if chg_name:
        pred_df_all.columns = [int(i.split('_')[2]) for i in pred_df_all.columns]        
    return pred_df_all

    ##############################


# config
# edate = '20221125'
version_name = 'arrow_prod'
model_date_dict = {'arrow_prod':'20221125'}
model_date = model_date_dict[version_name]

model_root = './models'

model_date = '20221125'
model_list = ['lr_cla','lasso_reg','lgbm_cla','lgbm_reg','mlp_reg','mlp_cla']
stack_model = 'lasso_reg'
# path setting
fac_path = './factors/factor_input.pkl'
#fac_path = '/data/user/000072/share/arrow_prod/factors/factor_input.pkl'
model_path_dict = {m:os.path.join(model_root,'%s.pkl'%(m)) for m in model_list}
stack_model_path = os.path.join(model_root,'stack_model','%s.pkl'%(stack_model))
model_path_dict

######
# read factor 
fac_val = pd.read_pickle(fac_path)

######
# read model ~ history result
model_dict = {m:read_pickle(model_path_dict[m]) for m in model_path_dict}
pred_raw_exist_dict = {m:model_dict[m]['prediction'].stack() for m in model_dict}
pred_raw_exist_df = pd.DataFrame(pred_raw_exist_dict)
stack_model_dict = read_pickle(stack_model_path)
pred_raw_exist_df['stack'] = pd.DataFrame(stack_model_dict['prediction'].stack(),columns=['stack'])

##################################

# print('collect model prediction result ~ %s ~ %s'%(version_name,today))
res_dict_model_dict = {}
pred_raw_dict = {}
get_all_pred = False # True: piece existing raw result, else just predict new result
x_test = fac_val.loc[today]
# model_save_root = os.path.join(model_root,edate)
model_list = ['lasso_reg','lr_cla','lgbm_cla','lgbm_reg','mlp_cla','mlp_reg']
for model in model_list:
    pred_raw_list ,pred_norm_list = [],[]
#     print('%s'%(model))
    model_save_itr = model_path_dict[model]
    pred = 'regression' if model.split('_')[1] == 'reg' else 'classification'
    if get_all_pred:
        pred_raw = pred_helper_wrapper(x_test, model_save_itr, pred, model).unstack()
    else:
        pred_raw = pred_one_helper(x_test, model_save_itr, pred, model).unstack()
    pred_raw_dict[model] = pred_raw.stack().iloc[:,0]
pred_raw_df = pd.DataFrame(pred_raw_dict)
#############################


#######################################################################################
### check prediction difference
# pred_diff = pred_raw_exist_df.reindex(index=pred_raw_df.index)  - pred_raw_df
# print(pred_diff.tail())
# print(pred_diff.abs().sum())

#######################################################################################
model = stack_model
model_save_itr = stack_model_path
x_test_stack = pred_raw_df[model_list]
pred = 'regression' if model.split('_')[1] == 'reg' else 'classification'
pred_stack = pred_one_helper(x_test_stack, model_save_itr, pred, model).unstack()
pred_raw_dict['stack'] = pred_stack.stack().iloc[:,0]
pred_raw_df = pd.DataFrame(pred_raw_dict)
# print(pred_raw_df.tail())

#######################################################################################
### check prediction difference
# pred_diff = pred_raw_exist_df.reindex(index=pred_raw_df.index)  - pred_raw_df
# print(pred_diff.tail())
# print(pred_diff.abs().sum())

#######################################################################################
####################################################################################################################################



####################生成交易文件###############################

threshold = 0.15    #绝对阈值
daily_max_num = 20    #每日最大买入上限
daily_min_num = 1    #每日最小买入下限
order_price = '1'    #委托价格
start_time = '93000'    #开始时间
end_time = '93500'    #结束时间
stop_time = '145600'    #终止时间
algo = 'tvol'    #算法
tvol_ratio = '25'   #跟量比例
order_interval = '1'    #下单间隔
withdraw_time = '1'    #撤单间隔
reorder_price = '99'    #补单价格



final_score = pred_raw_df['stack']
final_score.to_pickle('./final_score.pkl')
buy_list = final_score[final_score > threshold].nlargest(daily_max_num).reset_index().Ticker.values 
num = len(buy_list)

if num > daily_min_num: 
    px = []
    for i in buy_list:
        data = pd.read_csv('./data/Transaction/' + i + '/' + today + '.csv')
        data = data.loc[(data.dt < today + ' 09:26:00') & (data.TradePrice > 0)].iloc[-1]
        lastpx = data.TradePrice
        px.append(lastpx)

    money_per_stock = 2000000
    qty = [int(round(x, -2)) for x in money_per_stock / np.array(px)]

    trade_list = pd.read_csv('trade_list.csv')
    buy_trade_list = pd.DataFrame([buy_list, 
                                   qty, 
                                   [order_price] * num,  
                                   ['B'] * num,  
                                   [start_time] * num,  
                                   [end_time] * num,  
                                   [stop_time] * num,  
                                   [algo] * num,  
                                   [tvol_ratio] * num,  
                                   [order_interval] * num,  
                                   [withdraw_time] * num,  
                                   [reorder_price] * num]).T 

    buy_trade_list.columns = trade_list.columns
    trade_list = pd.concat([trade_list, buy_trade_list])
    trade_list.to_csv('trade_list.csv', index = False)
###############################################################

