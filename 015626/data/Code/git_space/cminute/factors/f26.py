from factor_generator import FactorGenerator
from operators import *

class f26(FactorGenerator):
    
    def __init__(self):
        required_columns=['close','high','low']
        lookback_bars=60
        super(f26, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        high = ts_max(df['high'], N)
        low = ts_min(df['low'], N)
        r = (high - low).replace(0, np.nan)
        hr = (high - df['close']) / r
        lr = (df['close'] - low) / r
        vwtc_r = ts_mean(lr, int(N / 2))
        vw = ts_mean(hr, int(N / 2))
        factor = -1 * (vwtc_r - vw)
        
        return factor.to_frame(name = self.__class__.__name__)