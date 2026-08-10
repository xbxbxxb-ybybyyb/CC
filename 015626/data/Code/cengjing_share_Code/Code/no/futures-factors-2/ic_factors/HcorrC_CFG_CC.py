import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
import datetime

class HcorrC_CFG_CC(FutureFactor):

    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 1
    data_dict = dict()
    instrument_type = 'recent'
    data_dict['Stock'] = ['close','weight','high', 'adjfactor']
    normalize_size = 1200 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):

        hhigh = data['high_preadj'].iloc[-61:]
        hclose = data['close_preadj'].iloc[-61:]
        hweight = data['weight'].iloc[-1:]
        s = hhigh.rolling(60, min_periods=30).std()
        f = hclose.rolling(60, min_periods=30).std()
        s[abs(s) < 1e-7] = np.nan
        f[abs(f) < 1e-7] = np.nan
        t_pcor2 = hhigh.rolling(60, min_periods=30).cov(hclose) / (s * f)

        t_pcor2[~np.isfinite(t_pcor2)] = 0
        
        factor = np.nanmean(t_pcor2.iloc[-1:]*hweight)
        return factor