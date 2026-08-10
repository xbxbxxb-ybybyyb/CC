import numpy as np
from future_factor import FutureFactor

class MinuteIndexTSCSStdRatio(FutureFactor):
    '''
    Description: ts_std(weighted_cs_mean(pct_chg(close, 1), w=index_weight), 60)
                / weighted_cs_std(ts_mean(pct_chg(close, 1), 60))
    Class: Price_TS_Stat
    Author: hefj, modified by lixr
    '''
    
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['weight','adjfactor', 'close']
    normalize_size = 5 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        
        lb = 60
        weight = data['weight'].values
        adjfactor = data['adjfactor'].values
        close = data['close'].values * adjfactor
        close[close == 0] = np.nan
        
        rtn_temp = close[-lb:] / close[-lb - 1: -1] - 1
        idx_rtn = np.nansum(rtn_temp * weight[-lb:], axis=1)
        ts_std = np.nanstd(idx_rtn)
        stk_rtn = np.nanmean(rtn_temp, axis=0)
        cs_mean = np.nansum(stk_rtn * weight[-1])
        cs_std = np.nansum(((stk_rtn - cs_mean) ** 2) * weight[-1]) ** 0.5
        
        return ts_std / cs_std