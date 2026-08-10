from future_factor import FutureFactor
import numpy as np


class MinuteVolumeAutoCorr_IH(FutureFactor):
    '''
    Description: corr(volume_ratio, shift(volume_ratio, 1), 60),
                 volume_ratio = volume[-240:] / mean(volume[-1440:-240].reshape(5, 240), axis=0)
    Class: Volume_Stat
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'recent'
    days_past = 7
    data_dict = {}
    data_dict['Continuous_Data'] = {'IH': ['volume']}
    normalize_size = 40 * 240
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        volume = data['volume_cont_IH'].values[-1440:]
        volume_ratio = volume[-240:] / np.nanmean(volume[:-240].reshape(5, 240), axis=0)
        f = np.corrcoef(volume_ratio[-60:], volume_ratio[-61:-1])[0, 1]
        return f
