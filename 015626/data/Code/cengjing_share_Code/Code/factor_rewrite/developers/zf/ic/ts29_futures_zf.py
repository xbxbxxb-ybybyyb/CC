import pandas as pd
import numpy as np
import bottleneck as bk
from future_factor import FutureFactor

class ts29_futures_zf(FutureFactor):
    '''
    期货类因子
    '''
    data_type = 'Future' # 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent' # 期货连续合约数据种类, 近月数据为'recent', 主力为'main'
    data_dict['Continuous_Data'] = {'IC':['close','volume']} #期货连续合约，处理了合约跳变问题
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'

    def calculate(self, data):
        close = data['close_cont_IC'].values[-240:]
        volume = data['volume_cont_IC'].values[-240:]
            
        fac = -1*(close[10:]-close[:-10])/close[:-10]*volume[10:]
        fac = (bk.move_rank(fac,window = 20, min_count = 10)+1)/2
        return np.nanmean(fac[-200:])