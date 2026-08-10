from factor_generator import FactorGenerator
from operators import *

class f15(FactorGenerator):
    
    def __init__(self):
        required_columns=['buy_amount','sell_amount','amount']
        lookback_bars=40
        super(f15, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        factor = -1 * ts_sum(df['buy_amount'] - df['sell_amount'], N) / ts_sum(df['amount'], N).replace(0, np.nan)
        
        return factor.to_frame(name = self.__class__.__name__)