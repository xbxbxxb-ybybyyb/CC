from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_ts419_cs_cfg_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close', 'high', 'low', 'volume', 'stk_index_corr_sh50', 'adjfactor'] 
    normalize_size = 5*242
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        close = df['close_preadj'][-40:]
        low = df['low_preadj'][-40:]
        high = df['high_preadj'][-40:]
        volume = df['volume_preadj'][-40:]
        
        cs = df['stk_index_corr_sh50'][-1:]
        
        factor = bk.move_sum(((close - low) - (high - close)) / (high - low) * volume, 10, 5, axis = 0)[-30:]
        finaldf = np.nanmean(factor, axis = 0)

        factor = finaldf * cs.values

        factor = np.nansum(factor, axis=1)
        return factor