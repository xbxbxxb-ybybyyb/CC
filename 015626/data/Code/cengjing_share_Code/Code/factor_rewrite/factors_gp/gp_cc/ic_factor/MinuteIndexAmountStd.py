from future_factor import FutureFactor
import numpy as np


class MinuteIndexAmountStd(FutureFactor):
    '''
    Description: std(close_000905.SH * volume_000905.SH, 20) / mean(close_000905.SH * volume_000905.SH, 90)
    Class: Liquidity
    Author: jinpx, modified by hefj
    '''
    data_type = 'Future'
    instrument_type = 'main'
    days_past = 1
    data_dict = {}
    data_dict['Index_Id'] = {'000905.SH': ['close', 'volume']}
    normalize_size = 40 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close_000905.SH'].values[-90:]
        volume = data['volume_000905.SH'].values[-90:]
        close_volume = close * volume
        f = np.nanstd(close_volume[-20:]) / np.nanmean(close_volume)
        return f
