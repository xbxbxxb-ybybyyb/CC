from factor_generator import FactorGenerator
from operators import *

class f2(FactorGenerator):
    
    def __init__(self):
        required_columns=['open','high','low','close']
        lookback_bars=50
        super(f2, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 40
        high = ts_max(df['high'], N)
        low = ts_min(df['low'], N)
        a = high - df['open'].shift(N)
        b = df['close'] - low
        c = (high - low) * 2
        c[abs(c) < 1e-8] = np.nan
        factor = -1 * (a + b) / c
        
        return factor.to_frame(name = self.__class__.__name__)