from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class RankinglistEffect(BaseFactor):
    
 
    factor_type = "DAY"
    depend_data = [ 'FactorData.Basic_factor.close_badj',
                    'FactorData.Basic_factor.is_valid']
                    

    lag = 1
    reform_window = 60

    def calc_single(self, database):

        close_badj = database.depend_data['FactorData.Basic_factor.close_badj']
        
        ret = pd.DataFrame(close_badj.values/close_badj.shift(1).values-1, index=close_badj.index, columns=close_badj.columns)
        ret_rank_desc = ret.rank(axis=1,ascending=False, method='first')
        up = pd.DataFrame(0, index=ret_rank_desc.index, columns=ret_rank_desc.columns)
        flag = pd.DataFrame(ret_rank_desc.values<=100, index=ret_rank_desc.index, columns=ret_rank_desc.columns)
        up[flag] = 1
        return -up.iloc[-1,]

    def decay(self, x):
        period = len(x)
        decay_days =10.0
        w = np.array([pow(pow(1/2,1/decay_days), period - 1 - i) for i in range(period)])
        w= w/sum(w)
        return np.sum(w*x)
        
        
    def reform(self,temp_result):
        factor = temp_result
        res = factor.rolling(self.reform_window,1).apply(self.decay) 
        return res