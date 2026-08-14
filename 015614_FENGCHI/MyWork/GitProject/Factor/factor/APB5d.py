from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class APB5d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume", 
                   "FactorData.Basic_factor.amt", 
                   "FactorData.Basic_factor.adjfactor", 
                "FactorData.Basic_factor.is_valid", ]
    
    lag = 4
    minute_lag = 0
    reform_window = 0
    
    def calc_single(self, database):
    
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        volume = database.depend_data['FactorData.Basic_factor.volume']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]
        
        
        vwap_adj = ((amt/volume)*adjfactor).fillna(method='ffill')
        volume_adj = (volume/adjfactor).fillna(0)
        
        vwap_adj_avg = vwap_adj.mean()
        vwap_adj_weightavg = (vwap_adj*volume_adj).sum()/volume_adj.sum()
                
        result = np.log(vwap_adj_avg/vwap_adj_weightavg)
        return result[valid]


        

    