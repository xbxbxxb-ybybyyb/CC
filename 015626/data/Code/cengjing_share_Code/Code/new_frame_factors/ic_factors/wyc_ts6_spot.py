import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd

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
    assert 0 < alpha < 1
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

class wyc_ts6_spot(FutureFactor):

    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 5
    data_dict = dict()
    data_dict['Index_Id'] = {'000905.SH':['close','high','low','volume']} 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    handle_preadj = None 
    
    def calculate(self, df):
        a = (df['high_000905.SH'] - df['low_000905.SH'])
        a[abs(a) < 1e-8] = np.nan
        b = df['volume_000905.SH'] * ((df['close_000905.SH'] - df['low_000905.SH']) - (df['high_000905.SH'] - df['close_000905.SH']))
        c = b / a
        factor = ts_truncated_ema(c, 800, 1/50)[-260:]
        factor = (bk.move_rank(factor.values, 100, min_count=50, axis = 0) + 1)/2
        factor = np.nanmean(factor[-160:])
        return factor