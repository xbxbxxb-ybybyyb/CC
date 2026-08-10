import numpy as np
import pandas as pd
from future_factor import FutureFactor


class MinuteBidAskVolPressure30Ema(FutureFactor):
    '''
    Description: -ema(SUM(BidVol, 30) / SUM(AskVol, 30), 5)
    Class:Bid_Ask
    Author: shentq modeified by liuz
    '''
    data_type='Future'
    instrument_type='main'
    days_past=1
    data_dict=dict()
    data_dict['Future_Data'] = ['AskVol', 'BidVol']
    
    normalize_size=5*237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):

        ask_vol = data['AskVol'].values 
        bid_vol = data['BidVol'].values 

        pressure_ema_list = []
        for i in range(59, -1, -1):
            ask_vol_sum = np.nansum(ask_vol[-30-i:][:30])
            bid_vol_sum = np.nansum(bid_vol[-30-i:][:30])
            if ask_vol_sum == 0:
                pressure = 0
            else:
                pressure = bid_vol_sum / ask_vol_sum
            pressure_ema = self.calc_ema(pressure_ema_list,pressure,5)
            pressure_ema_list.append(pressure_ema)

        factor = -pressure_ema_list[-1]

        return factor
    
    def calc_ema(self, cur_ema_list,x_n,span=None):
        cur_ema_length = len(cur_ema_list)

        if span == None:
            span = cur_ema_length + 1
        else:
            span = min(cur_ema_length+1,span)
            assert span > 0, "Invalid input of arg span!"

        alpha = 2 / (span+1)

        if cur_ema_length == 0:
            return x_n
        else:
            return (alpha * x_n + (1-alpha) * cur_ema_list[-1])
