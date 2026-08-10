import numpy as np
from future_factor import FutureFactor

class MinuteVolumeShrinkReturn(FutureFactor):
    '''
    Description: 
    Class: PV_Corr
    Author: liuz, modified by jinpx
    '''    
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 6
    data_dict = dict()
    data_dict['Future_Data'] = ['close']
    data_dict['Other_Future_Instrument'] = {'00':['volume'], '01':['volume'], '02':['volume'], '03':['volume']}
    normalize_size = 1 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
                
        close = data['close'].values
        volume_00 = data['volume_00'].values
        volume_01 = data['volume_01'].values
        volume_02 = data['volume_02'].values
        volume_03 = data['volume_03'].values
        
        volume = (volume_00 + volume_01 + volume_02 + volume_03)
        r = (close[5:] - close[:-5]) / close[:-5]
        volume_ratio = volume[-240:] / np.nansum(volume[-1440:-240].reshape(5, 240), axis=0)
        volume_ratio_change = volume_ratio[5:] - volume_ratio[:-5]
        f = np.nanmean(r[-60:][volume_ratio_change[-60:]<0])
        if np.isnan(f):
            f = 0
        
        return f