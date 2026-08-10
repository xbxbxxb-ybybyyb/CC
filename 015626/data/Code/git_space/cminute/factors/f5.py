from factor_generator import FactorGenerator
from operators import *

class f5(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=50
        super(f5, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 40
        temp = df['close'].diff()
        down = temp.copy()
        temp[temp < 0] = 0
        down[down > 0] = 0
        factor = ts_sum(temp, N) / ts_sum(down, N) 
        
        return factor.to_frame(name = self.__class__.__name__)