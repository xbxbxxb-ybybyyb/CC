from factor_generator import FactorGenerator
from operators import *

class f12(FactorGenerator):
    
    def __init__(self):
        required_columns=['close']
        lookback_bars=130
        super(f12, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        f5 = ts_mean(df['close'], 5).diff()
        f10 = ts_mean(df['close'], 10).diff()
        f30 = ts_mean(df['close'], 30).diff()
        f60 = ts_mean(df['close'], 60).diff()
        f120 = ts_mean(df['close'], 120).diff()
        factor = -1 * (f5 + f10 + f30 + f60 + f120)
        
        return factor.to_frame(name = self.__class__.__name__)