from factor_generator import FactorGenerator
from operators import *

class f10(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=50
        super(f10, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 40
        factor = rsi(df['close'], N) * -1
        
        return factor.to_frame(name = self.__class__.__name__)