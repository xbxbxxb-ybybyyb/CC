from factor_generator import FactorGenerator
from operators import *

class f13(FactorGenerator):
    
    def __init__(self):
        required_columns=['close', 'amount']
        lookback_bars=30
        super(f13, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 20
        ret = df['close'].pct_change(N)
        factor = -1 * ret / ts_sum(df['amount'], N)
        
        return factor.to_frame(name = self.__class__.__name__)