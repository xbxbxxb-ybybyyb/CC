from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd
from joblib import Parallel, delayed

def rolling_window(a, window):
    # 把数组展开成需要的rolling窗口, 只接受一维数组
    shape = a.shape[:-1] + (a.shape[-1] - window + 1, window)
    strides = a.strides + (a.strides[-1],)
    rolling_table = np.array(np.lib.stride_tricks.as_strided(a, shape=shape, strides=strides))
    return rolling_table
    
def ts_truncated_ema(df1, d, alpha):
    # truncated ema
    if isinstance(df1, pd.DataFrame):
        assert df1.shape[1] == 1
        df1 = df1[df1.columns[0]]
            
    assert isinstance(df1, pd.Series), 'the data structure of input is illegal, must be series'
    assert 0 < alpha <1
    df1_copy = df1.copy()
    weight = np.append(alpha * np.array([(1 - alpha) ** i for i in range(d - 1)]), (1 - alpha) ** (d - 1))[::-1]
    output = pd.Series(np.nan, index=df1_copy.index, name=df1_copy.name)
    temp_y = rolling_window(df1_copy, d)
    temp_x = np.tile(weight, (temp_y.shape[0], 1))
    flag = np.isnan(temp_x) | np.isnan(temp_y)
    flag1 = np.sum(np.isnan(flag), axis=1)  # 缺失值个数
    flag1 = np.where(flag1 <= int(d / 2), 1, np.nan)
    temp_x[flag] = np.nan
    temp_y[flag] = np.nan
    output.iloc[d - 1:] = (np.nansum(temp_y * temp_x, axis=1) / np.nansum(temp_x, axis=1)) * flag1
    return output

def multi_processing_joblib(df, func, n_jobs=12, **kwargs):
    assert isinstance(df, pd.DataFrame), 'the data structure of input is illegal, must be dataframe'
    results = Parallel(n_jobs=n_jobs)(delayed(func)(df[i], **kwargs) for i in df.columns)
    results_df = pd.DataFrame(results, index=df.columns, columns=df.index)
    return results_df.T

class wyc_ts6_future_ar_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close', 'amount', 'high', 'low', 'volume', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[0,1]'
    handle_preadj = True 

    def calculate(self, df):
        a = df['high_preadj'][-1535:] - df['low_preadj'][-1535:]
        a[abs(a) < 1e-8] = np.nan
        factor = df['volume_preadj'][-1535:] * ((df['close_preadj'][-1535:] - df['low_preadj'][-1535:]) - (df['high_preadj'][-1535:] - df['close_preadj'][-1535:])) / a
        factor = multi_processing_joblib(df=factor, func=ts_truncated_ema, n_jobs=-1, d=200, alpha= 1/45).values[-1335:]
        factor = bk.move_rank(factor, 1200, 600, axis = 0)[-135:]
        factor = bk.move_mean(factor, 15, 7, axis = 0)[-120:]

        a = df['amount'][-120:]
        ar = (2 * a.rank(axis=1, pct=True) - 1).values
        
        factor = factor * ar
        factor = np.nansum(factor,axis=1)

        factor = bk.move_rank(factor, 100, 50, axis = 0)[-20:]
        factor = np.nanmean(factor)

        return factor