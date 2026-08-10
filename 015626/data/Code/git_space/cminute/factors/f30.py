from factor_generator import FactorGenerator
from operators import *

class f30(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=40
        super(f30, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        M = 5
        N = 30
        ma1 = ts_mean(df['close'], M)
        ma2 = ts_mean(df['close'], N)
        factor = 1 - ma1 / ma2
        
        return factor.to_frame(name = self.__class__.__name__)