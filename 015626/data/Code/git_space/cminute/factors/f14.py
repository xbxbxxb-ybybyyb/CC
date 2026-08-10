from factor_generator import FactorGenerator
from operators import *

class f14(FactorGenerator):
    
    def __init__(self):
        required_columns=['close','high']
        lookback_bars=70
        super(f14, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        high = df['high']
        close = df['close']
        low = df['close']
        temp = ts_max(high, N) - ts_min(low, N)
        temp = temp.replace(0, np.nan)
        hh = (ts_max(high, N) - close) / temp
        aa = (close - ts_min(low, N))/temp
        factor = hh - aa
        
        return factor.to_frame(name = self.__class__.__name__)