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

class wyc_ts6_spot_if(FutureFactor):
    data_type = 'Future'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Index_Id'] = {'000300.SH':['close','high','low','volume']}
    normalize_size = 1210 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, df):
        close = df['close_000300.SH'][-460:]
        high = df['high_000300.SH'][-460:]
        low = df['low_000300.SH'][-460:]
        volume = df['volume_000300.SH'][-460:]
        
        a = high- low
        b = volume * ((close - low) - (high - close))
        c = b / a
        c = c.replace([np.inf, -np.inf], np.nan)
        
        factor = ts_truncated_ema(c, 200, 1/20)[-260:].values
        factor = bk.move_rank(factor, 240, 120, axis = 0)[-20:]
        factor = np.nanmean(factor)

        return factor