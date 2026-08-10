from commodity_framework import FutureFactor

from operators_cc_com import *
from rolling_adj import *
from numba import njit

import numpy as np
def replace_zero(x):
    if isinstance(x, float):
        if np.abs(x) < 1e-8:
            x = np.nan
    elif isinstance(x, np.ndarray):
        x = np.where(np.abs(x) > 1e-8, x, np.nan)
    else:
        raise TypeError(type(x))
    return x

from utils_zsj import SMA


def rolling_normalize_array(sig, window):

    sig_max = move_max_bk(sig,window,min_count = int(window/2))

    sig_min = move_min_bk(sig,window,min_count = int(window/2))

    sig_roll_norm = (sig - sig_min) / (sig_max - sig_min) * 2 - 1

    return sig_roll_norm

class fac_63_2_orig_1min_df_20x_noroll_(FutureFactor):
    
    def __init__(self, ticker, freq):

        super().__init__()
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 5
        self.required_columns = ['close_secmain']
        self.normalize_size = 240
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__       
        self.factor_list = []
    
    def calculate(self, data):
        aaa = 100
        bbb = 700
        ccc = 250
        ddd = 10
        dclose = data['close_secmain'][-int(np.sqrt(aaa)) * 100:]
        
        price_level = rolling_norm_raw(dclose, int(np.sqrt(aaa)) * 100)
        price_std = nanstd_np(dclose[-bbb: ], ddof = 1)
        factor = (price_level / r(price_std))
        self.factor_list.append(factor)
        ema_win = int(np.sqrt(ccc))
        
        factor1 = ema_1(self.factor_list[-ema_win * 3: ], ema_win * 3, 1 / (ema_win + 1))
        return factor1

    def pre_calculate(self, data):
        aaa = 100
        bbb = 700
        ccc = 250
        ddd = 10

        for i in range(40, -1, -1):
            if i == 0:
                dclose = data['close_secmain'][-int(np.sqrt(aaa)) * 100:]
            else:
                dclose = data['close_secmain'][-int(np.sqrt(aaa)) * 100 - i: -i]
                
            try:
                price_level = rolling_norm_raw(dclose, int(np.sqrt(aaa)) * 100)

                #price_level = rolling_norm(data['close'], 100 * int(np.sqrt(aaa))).fillna(method = 'ffill')
                price_std = nanstd_np(dclose[-bbb: ], ddof = 1)
                factor = (price_level / r(price_std))
                self.factor_list.append(factor)
            except:
                if len(factor_list) > 0:
                    self.factor_list.append(self.factor_list[-1])
                else:
                    self.factor_list.append(np.nan)
                        
