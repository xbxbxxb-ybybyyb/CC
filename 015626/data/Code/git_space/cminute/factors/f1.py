from factor_generator import FactorGenerator
from operators import *

class f1(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=50
        super(f1, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 40
        r = df['close'].pct_change()
        factor = -1 * ts_mean(r, N) / ts_std(r, N)
        
        return factor.to_frame(name = self.__class__.__name__)