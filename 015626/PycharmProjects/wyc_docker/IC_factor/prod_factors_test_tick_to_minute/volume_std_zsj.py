# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""
class volume_std_zsj(FactorGenerator):
    def __init__(self):
        super(volume_std_zsj, self).__init__(factor_name = 'volume_std_zsj',
                                                required_columns = [ 'close','volume'],
                                                lookback_bars = 1400)

    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa
    
    def on_bar(self, data):
        # def data
        volume = data['volume']
        close = data['close']
        # calc
        std_win = 30
        volume_std_raw = volume.rolling(std_win).std()
        volume_std = self.normalization(volume_std_raw.to_frame())
        volume_std.index = data.index
        volume_std.columns = [self.__class__.__name__]
        ##### format factor #####
        
        factor = volume_std.copy()
        factor[factor<=-0.5] = np.nan
        return factor

