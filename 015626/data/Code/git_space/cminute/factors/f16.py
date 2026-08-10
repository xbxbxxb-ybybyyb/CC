from factor_generator import FactorGenerator
from operators import *

class f16(FactorGenerator):
    
    def __init__(self):
        required_columns=['open','high','low','close']
        lookback_bars=40
        super(f16, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        mm = ts_mean(df['close'], N) + ts_mean(df['open'], N) + ts_mean(df['high'], N) + ts_mean(df['low'], N)
        factor = -1 * mm.pct_change()
        
        return factor.to_frame(name = self.__class__.__name__)