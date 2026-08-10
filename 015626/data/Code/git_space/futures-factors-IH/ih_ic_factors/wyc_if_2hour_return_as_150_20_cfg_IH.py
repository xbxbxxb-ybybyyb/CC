import numpy as np
from future_factor import FutureFactor
import bottleneck as bk
import pandas as pd
 
class wyc_if_2hour_return_as_150_20_cfg_IH(FutureFactor):
    data_type = 'IndexStock' 
    instrument_type = 'recent'
    days_past = 2
    data_dict = dict()
    data_dict['Stock'] = ['close','amount','adjfactor']
    normalize_size = 5*242
    normalize_type = 'ts_rank' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = True

    def calculate(self, df):
        cif = df['close_preadj'].values
        cif[abs(cif) < 1e-8] = np.nan
        ifreturn = cif[1:] / cif[:-1] - 1
        factor = bk.move_mean(ifreturn, 200, min_count=100, axis = 0)

        a = df['amount'].values
        factor = factor * a[1:]
        factor = np.nansum(factor,axis = 1)

        factor = bk.move_rank(factor[-170:], 150, 25, axis = 0)
        factor = np.nanmean(factor[-20:])

        return factor