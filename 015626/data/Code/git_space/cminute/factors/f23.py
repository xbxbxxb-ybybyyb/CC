from factor_generator import FactorGenerator
from operators import *

class f23(FactorGenerator):
    
    def __init__(self):
        required_columns=['close','buy_amount','sell_amount']
        lookback_bars=40
        super(f23, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 30
        flag = np.sign(df['close'].pct_change())
        factor = pd.concat([df['buy_amount'][flag > 0], df['sell_amount'][flag < 0] * -1], axis = 1).sum(axis = 1)
        factor = -1 * ts_sum(factor, N) 
        
        return factor.to_frame(name = self.__class__.__name__)