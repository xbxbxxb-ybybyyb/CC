from factor_generator import FactorGenerator
from operators import *

class f8(FactorGenerator):
    
    def __init__(self):
        required_columns=['volume','high','low','close']
        lookback_bars=70
        super(f8, self).__init__(required_columns=required_columns, lookback_bars=lookback_bars)

    def on_bar(self, df):

        N = 60
        typical = (df['high'] + df['low'] + df['close']) / 3
        mf = df['volume'] * typical
        volume_sum = ts_sum(df['volume'], N)
        volume_sum[abs(volume_sum)<1e-8] = np.nan
        mf_sum = ts_sum(mf, N)
        vwap_val = mf_sum / volume_sum
        factor = vwap_val - df['close']
        
        return factor.to_frame(name = self.__class__.__name__)