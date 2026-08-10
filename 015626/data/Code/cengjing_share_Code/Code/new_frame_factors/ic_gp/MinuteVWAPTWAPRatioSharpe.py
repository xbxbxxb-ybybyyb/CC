import numpy as np
from future_factor import FutureFactor

class MinuteVWAPTWAPRatioSharpe(FutureFactor):
    '''
    Description: mean(((amount / volume / 200) - twap) / ((amount / volume / 200) + twap), 120)
    Class: Return_Risk
    Author: hefj, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = dict()
    data_dict['Future_Data'] = ['amount', 'volume', 'twap']
    normalize_size = 5 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        amount = data['amount'].values
        volume = data['volume'].values
        twap = data['twap'].values
        
        vwap = amount / volume
        vwap_twap_ratio = (vwap - twap) / (vwap + twap)

        N = 120
        f = np.nanmean(vwap_twap_ratio[-N:]) / np.nanstd(vwap_twap_ratio[-N:])
        
        return f