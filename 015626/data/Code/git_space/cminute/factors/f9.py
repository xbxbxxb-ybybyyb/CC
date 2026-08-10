from factor_generator import FactorGenerator
from operators import *

class f9(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=40
        super(f9, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        factor = -1 * up_down_ratio(df['close'], N)
        
        return factor.to_frame(name = self.__class__.__name__)