from factor_generator import FactorGenerator
from operators import *

class f25(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=70
        super(f25, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        hret = df['close'].pct_change()
        hlong = hret > 0
        factor = ts_sum(hlong, N) * -1
                
        return factor.to_frame(name = self.__class__.__name__)