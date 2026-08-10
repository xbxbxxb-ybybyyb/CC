from future_factor import FutureFactor
import numpy as np


class wyc_bigon_cfghf(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['BuyUniqueOrderNum','BuyTradeNum']
    normalize_size = 5 * 242 
    normalize_type = 'ts_rank' 
    num_range = None 
    handle_preadj = None
  

    def calculate(self, df):
        
        btn = df['BuyTradeNum'].values[-14:]
        btn[abs(btn) < 1e-8] = np.nan
        factor = 1 - df['BuyUniqueOrderNum'].values[-14:] / btn

        factor = np.nansum(factor, axis =1)
        factor = np.nanmean(factor)
        return factor