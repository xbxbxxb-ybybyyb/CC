import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import scipy
from joblib import Parallel, delayed

def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    # 这是后面算子计算的辅助函数
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides)
    return rolling_table

    
def get_top_mean(df1, d):
    output = pd.Series(np.nan, index=df1.index)
    a = rolling_window(df1, d)
    b = np.sort(a)
    c = np.nanmean(b[:,-5:], axis=1)
    flag = np.sum(np.isnan(a), axis=1) 
    flag = np.where(flag <= d - int(d / 2), 1, np.nan)
    output.iloc[d - 1:] = c * flag
    return output


def multi_processing(df, func, n_jobs, **kwargs):
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

class stk2idx_maxret_diff_chg_zsj_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close','adjfactor']
    normalize_size = 1200
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, data):
        ## prep data
        stk_close = data['close_preadj'][-101:]
        stk_ret = stk_close / stk_close.shift(1) - 1

        stk_max_ret = multi_processing(df=stk_ret, func=get_top_mean, n_jobs=1, d=60)

        stk_ret_duration = stk_close/stk_close.shift(5) - 1 
        stk_maxret_diff = stk_max_ret - (stk_ret_duration/5)
        stk_maxret_diff[~np.isfinite(stk_maxret_diff)] = np.nan
        stk2idx_maxret_diff_raw = np.nanmean(stk_maxret_diff[-30:].values, axis=1)
        factor = np.nanmean(stk2idx_maxret_diff_raw[-10:]) - np.nanmean(stk2idx_maxret_diff_raw)  
        
        return factor