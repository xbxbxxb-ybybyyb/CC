from factor_generator import FactorGenerator
from operators import *

class f6(FactorGenerator):
    
    def __init__(self):
        required_columns=['open','high','low','close']
        lookback_bars=50
        super(f6, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 40
        x = ts_max(df['high'], N) - ts_min(df['low'], N)
        x[abs(x)<1e-8] = np.nan
        factor = -1 * (df['close'] - df['open'].shift(N)) / x
        
        return factor.to_frame(name = self.__class__.__name__)