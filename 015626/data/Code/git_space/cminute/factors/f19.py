from factor_generator import FactorGenerator
from operators import *

class f19(FactorGenerator):
    
    def __init__(self):
        required_columns=['close', 'volume']
        lookback_bars=30
        super(f19, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 20
        factor = -1 * ts_corr(df['close'].pct_change(), df['volume'], N)
        
        return factor.to_frame(name = self.__class__.__name__)