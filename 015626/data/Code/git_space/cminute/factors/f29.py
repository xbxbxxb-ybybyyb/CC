from factor_generator import FactorGenerator
from operators import *

class f29(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=70
        super(f29, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        factor = df['close'] / ts_mean(df['close'], N)
        factor = -1 * factor.pct_change(N)
                
        return factor.to_frame(name = self.__class__.__name__)