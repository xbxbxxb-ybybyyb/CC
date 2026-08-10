from factor_generator import FactorGenerator
from operators import *

class f24(FactorGenerator):
    
    def __init__(self):
        required_columns=['close','high','low']
        lookback_bars=40
        super(f24, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        factor = ts_max(df['high'], N) / ts_min(df['low'], N) - 1
        factor = -1 * factor * np.sign(df['close'].diff(N))
        
        return factor.to_frame(name = self.__class__.__name__)