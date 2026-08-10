from ts_factor.factor_generator import FactorGenerator
from ts_factor.operators import *
class wyc_ts1_future(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'volume']
        lookback_bars=65
        super(wyc_ts1_future, self).__init__(required_columns=required_columns,lookback_bars=lookback_bars)

    def on_bar(self, df):
        idx = df.index
        df = df.sort_index()
        factor = (-1 * correlation(df['close'], df['volume'], 60))

        factor = factor.to_frame()
        factor.columns = [self.__class__.__name__]
        return factor