from factor_generator import FactorGenerator
from operators import *

class f7(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=160
        super(f7, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        future_close = df['close']
        dpo = future_close - ts_delay(ts_mean(future_close, N), int(N/2+1))
        factor = ts_median(dpo, N) - dpo
                
        return factor.to_frame(name = self.__class__.__name__)