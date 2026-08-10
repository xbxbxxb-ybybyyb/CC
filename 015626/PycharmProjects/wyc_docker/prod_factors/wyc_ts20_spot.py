from factor_generator import FactorGenerator
from operators_wyc import *
import pandas as pd
import numpy as np
class wyc_ts20_spot(FactorGenerator):
    def __init__(self):

        required_columns=['close_spot','low_spot','high_spot','volume_spot']
        lookback_bars=2000
        super(wyc_ts20_spot, self).__init__(
                                  required_columns=required_columns,
                                  lookback_bars=lookback_bars)
    
    def normalization(self, signal, holding_window = 1200): 
        max_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).max()  
        min_s = signal.rolling(holding_window,min_periods=int(holding_window/2)).min() 
        a = (signal - min_s)/(max_s-min_s)
        a = 2*a-1
        aa = pd.DataFrame(a)
        aa.index = signal.index
        aa.columns = signal.columns
        return aa

    def on_bar(self, df):
        
        factor = ts_sum(((df.close_spot-df.low_spot)-(df.high_spot-df.close_spot))/(df.high_spot-df.low_spot)*df.volume_spot, 20)
        factor = mean(factor, 5)
        factor = ts_rank(factor, 4*242)
        factor = mean(factor, 20)

        factor = factor.to_frame()

        columnname = self.__class__.__name__
        factor.columns = [columnname]
        factor = factor.fillna(method='ffill')
        factor = self.normalization(factor, 4 * 242)
        return factor