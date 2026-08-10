from factor_generator import FactorGenerator
from operators import *

class f3(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=70
        super(f3, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        close = df['close']
        factor = -1 * (2 * close - ts_min(close, N) - ts_max(close, N))
        
        return factor.to_frame(name = self.__class__.__name__)