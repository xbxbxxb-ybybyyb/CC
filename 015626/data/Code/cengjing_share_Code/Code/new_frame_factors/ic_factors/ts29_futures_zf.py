import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

def get_norm(fa):
    fmax = np.nanmax(fa)
    fmin = np.nanmin(fa)
    divisor = fmax - fmin
    if divisor < 1e-8:
        divisior = np.nan
    return ((fa[-1] - fmin)/ divisor) * 2 - 1

class ts29_futures_zf(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' # 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    instrument_type = 'recent' # 期货连续合约数据种类, 近月数据为'recent', 主力为'main'
    data_dict['Continuous_Data'] = {'IC':['close','volume']} #期货连续合约，处理了合约跳变问题
    normalize_size = 0 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_cont_IC'].values[-1440:]
        volume = data['volume_cont_IC'].values[-1440:]
            
        fac = -1*(close[10:]-close[:-10])/close[:-10]*volume[10:]
        fac = (bk.move_rank(fac,window = 20, min_count = 10)[-1410:]+1)/2
        fac = bk.move_mean(fac,200,100,axis = 0)[-1210:]
        return get_norm(fac)