import pandas as pd
import numpy as np
import pickle
from joblib import Parallel, delayed
import os



def get_max_drawdown(ret_list, type='cumsum'):
    """
    calculate max drawdown, start date and end date of the max drawdown
    :param ret_list: array_like, one dimension
        yield curve or cumulative yield curve
    :param type: str
        可选cumsum或share，对应的输入分别是累计收益和分笔收益
    :return: float, datetime, datetime
        max_drawdown, max_drawdown_start_time, max_drawdown_end_time
    """
    assert isinstance(ret_list, pd.Series) or isinstance(ret_list, np.ndarray) or isinstance(ret_list, list)
    if isinstance(ret_list, np.ndarray):
        assert ret_list.shape[1] == 1
    if any([isinstance(ret_list, np.ndarray), isinstance(ret_list, list)]):
        ret_list = pd.Series(ret_list)
    if type == 'time_share':
        ret_list = ret_list.cumsum()
    ret_list1 = ret_list.expanding().max()
    ret_list2 = ret_list - ret_list1
    max_drawdown = ret_list2.min()
    if max_drawdown == 0:
        print('no drawdown')
        return
    else:
        max_drawdown_end_time = ret_list2.argmin()
        max_drawdown_start_time = ret_list[:ret_list2.argmin()].argmax()
        return max_drawdown, max_drawdown_start_time, max_drawdown_end_time



def multi_processing_joblib(df, func, n_jobs=12, **kwargs):
    """
    cross-section multi-process for the dataframe
    :param df: dataframe
        the raw data
    :param func:
        the function acting on dataframe
    :param n_jobs: int
        the number of cores used, if n_jobs=-1, all cores will be used
    :param kwargs:
        the parameters in the param func.
    :return: dataframe
        the data after the use of function
    """
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs, max_nbytes='1G')(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T


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
        'the data structure of input is illegal'
    data[abs(data) < 1e-8] = x
    return data


def pd_writer(sig, savepath):
    """
    把df写成h5文件并保存
    : param sig: dataframe
        待写入和保存的df
    : param savepath: str
        保存路径
    : return: None
    """
    sig_name = sig.columns[0]
    file_name = os.path.join(savepath, sig_name + '.h5')
    if os.path.exists(file_name):
        #sigold = IO.read_data(alt = file_name)
        sigold = pd.read_hdf(file_name)
        sigold = sigold[~sigold.index.isin(sig.index)]
        signew = pd.concat([sigold, sig], axis=0).sort_index()
    else:
        signew = sig
    signew.to_hdf(file_name, key=sig_name)


def read_pickle(save_path):
    with open(save_path, 'rb') as input:
        save_dict = pickle.load(input)
    return save_dict


def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    # 这是后面算子计算的辅助函数
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table


def save_pickle(save_dict, save_path):
    with open(save_path, 'wb') as input:
        pickle.dump(save_dict, input, protocol=pickle.HIGHEST_PROTOCOL)
    return