from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts419_ar_cfg(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'amount', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
#    num_range = '[-0.5,1]'
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-60:]
        low = df['low_preadj'][-60:]
        high = df['high_preadj'][-60:]
        volume = df['volume_preadj'][-60:]
        
        amount = df['amount'][-20:]
        
        factor = bk.move_sum(((close - low) - (high - close)) / (high - low) * volume, 10, 5, axis = 0)[-50:]
        finaldf = bk.move_mean(factor, 30, 15, axis = 0)[-20:]

        factor = finaldf * (2 * amount.rank(axis=1, pct=True).values - 1)

        factor = np.nansum(factor, axis=1)
        factor = np.nanmean(factor)

        return factor