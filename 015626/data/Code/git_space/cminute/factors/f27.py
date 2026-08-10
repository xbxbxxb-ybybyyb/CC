from factor_generator import FactorGenerator
from operators import *

class f27(FactorGenerator):
    
    def __init__(self):
        required_columns=['close','amount','trade_num']
        lookback_bars=40
        super(f27, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        factor = -1 * ts_sum(df['amount'],N) / ts_sum(df['trade_num'], N) * np.sign(df['close'].diff(N))
        
        return factor.to_frame(name = self.__class__.__name__)