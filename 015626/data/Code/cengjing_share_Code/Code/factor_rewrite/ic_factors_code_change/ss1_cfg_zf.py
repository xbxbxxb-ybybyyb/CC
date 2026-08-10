import bottleneck as bk
import numpy as np
from future_factor import FutureFactor

class ss1_cfg_zf(FutureFactor):
    '''
    成分股因子
    '''
    data_type = 'IndexStock'# 成分股为'IndexStock' 期货与指数为'Future'
    days_past = 7
    data_dict = dict()
    data_dict['Stock'] = ['close','high','amount','adjfactor']
    normalize_size = 242*5 # normalize所用历史数据长度
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None # normalize后因子取值范围，不在此范围内则置0,还可支持'()'表示开区间,默认为None表示[-1,1]
    handle_preadj = True # 表示对成分股进行前复权, 目前只复权open high low close volume字段，使用前复权后，因子逻辑中上述字段需增加'_preadj'后缀
    
    def calculate(self, data):
        close = data['close_preadj'].values[-242*6:]
        rtn = close[1:]/close[:-1]-1
        vol = bk.move_std(rtn, window = 60, min_count = 30, axis = 0)
        vol[vol < 1e-8] = 0
        high = data['high_preadj'].values[-242*6:]
        hh = bk.move_max(high[:-1],window = 60, min_count=30,axis=0)
        ret = close[1:]/hh-1
        facorg = ret/vol
        fac_max = bk.move_max(facorg, window = 242*5, min_count = 121*5, axis=0)
        fac_min = bk.move_min(facorg, window = 242*5, min_count = 121*5, axis=0)
        tmp = fac_max-fac_min
        tmp[np.abs(tmp)<1e-8]=np.nan
        facorg = (facorg-fac_min)/tmp*2-1

        amt_rank = (data['amount'].iloc[-5:].rank(axis=1,pct=True))*2-1
        ar = amt_rank.values
        fac = np.nansum(facorg[-5:]*ar,axis=1)
        return np.nanmean(fac)