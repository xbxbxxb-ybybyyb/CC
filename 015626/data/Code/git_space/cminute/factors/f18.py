from factor_generator import FactorGenerator
from operators import *

class f18(FactorGenerator):
    
    def __init__(self):
        required_columns=['open','high','low','close']
        lookback_bars=70
        super(f18, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        # 上影线-下影线
        factor = ts_max(df['high'], N) / max2(df['close'], df['open'].shift(N-1)) - min2(df['close'], df['open'].shift(N-1)) / ts_min(df['low'], N)
        
        return factor.to_frame(name = self.__class__.__name__)