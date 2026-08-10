from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
import numpy as np


class hnl_fac_ms_12_df(FutureFactor):
    
    def __init__(self, ticker, freq):
        super().__init__()
        self.ticker = ticker
        self.freq = freq
        
        self.days_past = int(1 * freq)
        self.required_columns = [ 'last_to_mid', 'dt']
        self.instrument_type = 'main' #second_main
        self.normalize_size = 500
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__
        self.fac_raw_list = []
        self.fac_list = []
    
    
    def itd(self, x):
        hour = x.astype('datetime64[h]').astype(int) % 24
        minute = x.astype('datetime64[m]').astype(int) % 60
        if (int(hour) > 9) & (hour < 15):
            return hour * 60 + minute * 1 - 9 * 60
        elif (int(hour <3)):
            return (hour + 24) * 60 + minute - 21 * 60
        else:
            return hour * 60 + minute * 1 - 21 * 60
    
    def calculate(self, data):

        ddt = np.array(data['dt'][-60:])

        ddt1 = [self.itd(item) for item in ddt]
        mk = nanargmin_new(ddt1) + 60


        factor = nanmean_np(data['last_to_mid'][-60:][mk:]) 
        if ('SC' in self.ticker) :
            factor = -factor
        return -factor
        
    def pre_calculate(self, data):
        pass




                
                


        