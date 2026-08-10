import datetime
import pandas as pd
import os, pickle
import numpy as np
from arrow.naming_config import *
from arrow.link_v2 import LinkMessage
import functools
import dill
import re
import bottleneck as bk
import json
import sched, time
import logging
import sys
from keras.models import load_model

def send_link(message):
    LinkMessage().sendMessage(str(message))

# 模型预测所用函数开始
def read_pickle(save_path=None,verbose=True):
    tic = time.time()
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    toc = time.time()
    return save_dict

def save_pickle(save_dict,save_path):
    print('saving data to:\n',save_path)
    folder = os.path.dirname(save_path)
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
    for model in model_list:
        model_pred = model_dict[model]['prediction']
        if isinstance(model_pred, pd.DataFrame):
            if model_pred.shape[1] > 1:
                model_pred = model_pred.stack()
        pred_list.append(model_pred)
    pred_df = pd.concat(pred_list, axis=1)
    pred_df.columns = model_list
    return pred_df

def pred_one_helper(x_test, res_base_path, model_name=None,chg_name=False):
    pred_df, model_dict_itr = get_model_pred_helper(res_base_path, model_name)
    pred_raw_list = []
    for k in model_dict_itr:
        pred = 'classification' if k.find('_cla')>0 else 'regression'
        path = res_base_path if k.find('mlp') >= 0 else None
        pred_raw_itr = pred_helper(x_test, model_dict_itr[k], pred=pred, res_base_path=path)
        pred_raw_list.append(pred_raw_itr)
    pred_df_all = pd.concat(pred_raw_list, axis=1)
    if chg_name:
        pred_df_all.columns = [int(i.split('_')[2]) for i in pred_df_all.columns]        
    return pred_df_all

# 模型预测所用函数结束

def np_clip(df, lower_bound, upper_bound):
    return pd.DataFrame(np.clip(df.values, lower_bound.values, upper_bound.values), index=df.index, columns=df.columns)

def mad(temp_factor, mad_threshold = 5):
    temp_mad = abs(temp_factor - temp_factor.median()).median()
    temp_median = temp_factor.median()
    down = temp_median - mad_threshold * temp_mad
    up = temp_median + mad_threshold * temp_mad
    temp_factor = np_clip(temp_factor, down, up)
    return (temp_factor - temp_factor.mean()) / replace_zero(temp_factor.std())

def rolling_norm_zscore(df):
    df = df.replace([-np.inf, np.inf], np.nan)
    for col in df:
        ub = df[col].mean() + 3*df[col].std()
        lb = df[col].mean() - 3*df[col].std()
        df.loc[df[col] > ub, col] = ub
        df.loc[df[col] < lb, col] = lb

    result = ((df - df.mean()) / df.std())
    return result

def scheduler(func, target_trigger_time, delay=0):
    # init func at given time with delay as in milliseconds
    assert isinstance(target_trigger_time, pd.Timedelta)
    assert callable(func)
    target_trigger_time = (pd.Timestamp(pd.Timestamp.now().date()) + target_trigger_time).to_pydatetime().timestamp() + delay / 1000
    s = sched.scheduler(time.time, time.sleep)
    s.enterabs(target_trigger_time, 0, func)
    s.run(blocking=True)


def read_json(path):
    with open(path, 'r') as fin:
        try:
            data = json.load(fin)
        except json.JSONDecodeError:
            data = None
    return data


def dump_json(path, value):
    with open(path, 'w') as fout:
        json.dump(value, fout, indent=4)



@functools.lru_cache(maxsize=None)
def ticker_match(ticker_num):
    ticker_num = int(ticker_num)
    suffix = '.SH' if ticker_num>=600000 else '.SZ'
    pre_fill = (6 - len(str(ticker_num)))*'0'
    ticker = pre_fill + str(ticker_num) + suffix
    return ticker





def diller(file_name, payload=None):
    if payload is None:
        with open(file_name, 'rb') as fin:
            return dill.load(fin)
    else:
        with open(file_name, 'wb') as fout:
            dill.dump(payload, fout, protocol=4)



def rolling_norm(sig, window):
    assert isinstance(sig, pd.Series) or isinstance(sig, pd.DataFrame), 'the data structure of input is illegal, must be series or dataframe'
    if window == 0:
        return sig
    else:
        if isinstance(sig, pd.DataFrame):
            sig_max = pd.DataFrame(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, columns=sig.columns)
            sig_min = pd.DataFrame(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                   index=sig.index, columns=sig.columns)
        elif isinstance(sig, pd.Series):
            sig_max = pd.Series(bk.move_max(sig, window=window, min_count=int(window / 2), axis=0),
                                index=sig.index, name=sig.name)
            sig_min = pd.Series(bk.move_min(sig, window=window, min_count=int(window / 2), axis=0),
                                index=sig.index, name=sig.name)
        temp = sig_max - sig_min
        temp[abs(temp) < 1e-8] = np.nan
        signal = (sig - sig_min) / temp
        return 2 * signal - 1


def ts_rank(df, window):
    # moving time-series rank for the past window periods
    assert isinstance(df, pd.Series) or isinstance(df, pd.DataFrame), 'input is not a dataframe or series'
    if window == 1:
        output = df
    else:
        if isinstance(df, pd.DataFrame):
            output = pd.DataFrame(bk.move_rank(df, window=window, min_count=int(window / 2), axis=0),
                                  index=df.index, columns=df.columns)
        elif isinstance(df, pd.Series):
            output = pd.Series(bk.move_rank(df, window=window, min_count=int(window / 2), axis=0),
                               index=df.index, name=df.name)
    return output


def replace_inf(data, x=np.nan):
    '''replace inf to a predefined number for the input data
    parameters
    --------------------------------------------------
    data: dataframe, series or ndarray
        the data which contains inf
    x: int, float or np.nan, optional (default=np.nan)
        the value used to replace inf
    --------------------------------------------------
    return
    --------------------------------------------------
    data: input data whose inf has been replaced
        the data whose inf is replaced
    --------------------------------------------------
    '''
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), 'the data structure of input is illegal'
    if isinstance(data, pd.Series) or isinstance(data, pd.DataFrame):
        data = data.replace([-np.inf, np.inf], x)
    elif isinstance(data, np.ndarray):
        data[np.isinf(data)] = x
    return data


def replace_zero(data, x=np.nan):
    """
    replace 0 to a predefined number for the input data
    :param data: dataframe, series or np.ndarray
        the data which contains 0
    :param x: int, float or np.nan, optional (default=np.nan)
        the value used to replace 0
    :return: same data structure as input data
        input data whose 0 has been replaced
    """
    assert isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray), \
        'the data structure of input is illegal, must be pd.Series, pd.DataFrame or np.ndarray'
    if isinstance(data, np.ndarray):
        data = data + 0.  # 下述转化对int类型的ndarray无效，因此事先将数据类型转为float
    data[abs(data) < 1e-8] = x
    return data


def ts_delay(data, d):
    # A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = np.empty_like(data)
        if d >= 0:
            output[d:] = data[:-d]
            output[:d] = np.nan
        else:
            output[:d] = data[-d:]
            output[d:] = np.nan

    else:
        output = data.shift(periods=d)
    return output


def ts_delta(data, d):
    # A_i - A_(i-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = data - ts_delay(data, d)
    else:
        output = data.diff(periods=d)
    return output


def ts_mean(data, d):
    # moving time-series mean for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_mean(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_mean(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_sum(data, d):
    # moving time-series sum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_sum(data, window=d, min_count=int(d / 2), axis=0)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_sum(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_std(data, d):
    # moving time-series rank for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1)
        if isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_std(data, window=d, min_count=int(d / 2), axis=0, ddof=1),
                               index=data.index, name=data.name)
    return output
    
    
def ts_pct_change(data, d=1):
    # (A_n - A_(n-d)) / A_(n-d)
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance (data, np.ndarray):
        output = np.full(data.shape, np.nan)
        output[d:] = ((data[d:]-data[:-d]) / replace_zero(data[:-d]))
    else:
        output = data.pct_change(d, fill_method=None)
    return output


def ts_median(data, d):
    # moving time-series meidan for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_median(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_median(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output


def ts_max(data, d):
    # moving time-series max for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if d == 1:
        output = data
    else:
        if isinstance(data, np.ndarray):
            output = bk.move_max(data, window=d, min_count=int(d / 2), axis=0)
        elif isinstance(data, pd.DataFrame):
            output = pd.DataFrame(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                                  index=data.index, columns=data.columns)
        elif isinstance(data, pd.Series):
            output = pd.Series(bk.move_max(data, window=d, min_count=int(d / 2), axis=0),
                               index=data.index, name=data.name)
    return output


def ts_min(data, d):
    # moving time-series minimum for the past d periods
    if not (isinstance(data, pd.Series) or isinstance(data, pd.DataFrame) or isinstance(data, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data, np.ndarray):
        output = bk.move_min(data, window=d, min_count=int(d / 2), axis=0)
    elif isinstance(data, pd.DataFrame):
        output = pd.DataFrame(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                              index=data.index, columns=data.columns)
    elif isinstance(data, pd.Series):
        output = pd.Series(bk.move_min(data, window=d, min_count=int(d / 2), axis=0),
                           index=data.index, name=data.name)
    return output


class VoidLogger:
    def debug(self, *args, **kwargs):
        pass

    def info(self, *args, **kwargs):
        pass

    def warning(self, *args, **kwargs):
        pass


def add_file_logger(name, level=None, file_name=None, mode='a',
                    format_str ='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    lazy_mode=False, void_flag=False):
    if void_flag:  # multiprocessing dummy
        return VoidLogger()
    logger = logging.getLogger(name)
    if lazy_mode:
        return logger
    if level is not None:
        logger.setLevel(level)
    else:
        logger.setLevel(logging.DEBUG)
    if file_name is not None:
        # if not logger.hasHandlers():
        _dirname = os.path.dirname(file_name)
        if len(_dirname) != 0 and not os.path.exists(_dirname):
            os.makedirs(_dirname)
        file_handler = logging.FileHandler(file_name, mode=mode)
        file_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(file_handler)
    else:
        # if not logger.hasHandlers():
            # default to screen
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(logging.Formatter(format_str))
        logger.addHandler(stream_handler)
    return logger



def get_single_minute_data(data, time):
    data_single_minute = data.iloc[data.index.indexer_at_time(time)]
    data_single_minute.index = pd.to_datetime(data_single_minute.index.date)
    data_single_minute.index.name = 'dt'
    return data_single_minute
    
    
def ts_corr(data1, data2, d):
    # data1, data2过去d条数据的时序相关系数
    if type(data1) != type(data2):
        raise TypeError('`data1` and `data2` must be the same type.')
    if data1.shape != data2.shape:
        raise ValueError('`data1` and `data2` must be the same shape.')
    if not (isinstance(data1, pd.Series) or isinstance(data1, pd.DataFrame) or isinstance(data1, np.ndarray)):
        raise TypeError('Only supports the following types: pd.Series, pd.DataFrame, np.ndarray')
    if isinstance(data1, np.ndarray):
        output = np.full(data1.shape, np.nan)
        data1_expanding = rolling_window_upgrade(data1, d)
        data2_expanding = rolling_window_upgrade(data2, d)
        flag = np.isnan(data1_expanding) | np.isnan(data2_expanding)
        flag1 = np.sum(flag, axis=-1)  # 缺失值个数
        flag2 = np.where(flag1 <= int(d / 2), 1, np.nan)
        data1_expanding[flag] = np.nan
        data2_expanding[flag] = np.nan
        data1_expanding_centralized = data1_expanding - np.nanmean(data1_expanding, axis=-1, keepdims=True)
        data2_expanding_centralized = data2_expanding - np.nanmean(data2_expanding, axis=-1, keepdims=True)
        output[d - 1:] = np.nansum(data1_expanding_centralized * data2_expanding_centralized, axis=-1) / np.sqrt(
            np.nansum(data1_expanding_centralized ** 2, axis=-1) * np.nansum(data2_expanding_centralized ** 2,
                                                                             axis=-1)) * flag2
    else:
        output = data1.rolling(d, min_periods=int(d / 2)).corr(data2)
        output.iloc[:d - 1] = np.nan
    return output