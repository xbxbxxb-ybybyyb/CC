from factor_generator import FactorGenerator
from operators import *

class f17(FactorGenerator):
    
    def __init__(self):
        required_columns=['vwap','amount','volume']
        lookback_bars=70
        super(f17, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        mm = ts_sum(df['amount'], N) / ts_sum(df['volume'], N)
        factor = df['vwap'] / mm * -1
        
        return factor.to_frame(name = self.__class__.__name__)