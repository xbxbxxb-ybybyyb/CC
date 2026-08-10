from future_factor import FutureFactor
import numpy as np
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

class wyc_ts38_spot_IM(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['close']}
    normalize_size = 5 * 242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        
        close = df['close_000852.SH'][-1360:]
        temp1 = close.copy()
        condition = close > close.shift(1)
        closestd = close.rolling(20, min_periods = 10).std()
        temp1[condition] = closestd
        temp1[~condition] = 0
        a = ts_truncated_ema(temp1[-1340:], 5 * 242, 1/100).values[-130:]

        temp1[condition] = 0
        temp1[~condition] = closestd
        b = ts_truncated_ema(temp1[-1340:], 5 * 242, 1/100).values[-130:]

        c = a + b
        c[abs(c) < 1e-8] = np.nan
        factor = a / c * 100
        factor = bk.move_rank(factor, 30, 15, axis = 0)[-100:]
        factor = np.nanmean(factor)
        return factor
