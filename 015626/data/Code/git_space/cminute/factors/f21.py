from factor_generator import FactorGenerator
from operators import *

class f21(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=130
        super(f21, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 120
        factor = -1 * ts_position(df['close'], N)
        
        return factor.to_frame(name = self.__class__.__name__)