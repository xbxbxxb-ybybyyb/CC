from factor_generator import FactorGenerator
from operators import *

class f11(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=40
        super(f11, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):
        
        N = 30
        mma = ts_mean(df['close'], N)
        factor = -1 * (df['close'] / mma - 1)
        
        return factor.to_frame(name = self.__class__.__name__)