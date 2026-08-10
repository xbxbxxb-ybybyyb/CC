from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

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

def delay(A,n):
    #A_(i-n)
    #A为df类型
    return A.shift(periods=n)

def ts_mean(A, d):
    # moving time-series average for the past d periods
    if isinstance(A, pd.Series):
        A = A.to_frame()
    output = pd.DataFrame(bk.move_mean(A, window=d, min_count=d//2, axis=0),
                          index=A.index, columns=A.columns)
    return output

class wyc_ts26_future_if(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 18
    data_dict = dict()
    data_dict['Continuous_Data'] = {'IF':['close']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, df):
        N = 6
        N1 = 4
        N2 = 8
        close = df['close_cont_IF'][-4223:]
        MTM = close - close.shift(1)
        MTMMA = ts_truncated_ema(MTM, 1200, 1/6)[-3022:]
        DIF = (ts_mean(delay(MTMMA, 1), 4) - ts_mean(delay(MTMMA, 1), 8))[-3014:]
        factor = ts_truncated_ema(DIF, 1200, 1/90)[-1814:]
        factor = bk.move_rank(factor, 484, 242, axis = 0)[-1330:]
        factor = bk.move_mean(factor, 120, 60, axis = 0)[-1210:]
        factor = get_norm(factor)
        
        return factor
