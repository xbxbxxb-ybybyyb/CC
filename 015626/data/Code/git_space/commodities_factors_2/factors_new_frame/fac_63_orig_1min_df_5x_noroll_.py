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

class fac_63_orig_1min_df_5x_noroll_(FutureFactor):
    
    def __init__(self, ticker, freq):

        super().__init__()
        self.ticker = ticker
        self.freq = freq
        self.days_past = int(freq) * 5
        self.required_columns = ['close_secmain']
        self.normalize_size = int(int(self.bars_dict[ticker] / freq) * 10)
        self.normalize_type = 'ts_rank'
        self.factor_name = self.__class__.__name__       
        self.factor_list = []
    
    def calculate(self, data):
        aaa = 50
        bbb = 225
        ccc = 20
        ddd = 10
        dclose = data['close_secmain'][-100 * int(np.sqrt(aaa)):]
        
        price_level = rolling_norm_raw(dclose, 100 * int(np.sqrt(aaa)))
        price_std = nanstd_np(dclose[-bbb: ], ddof = 1)
        factor = (price_level / r(price_std))
        self.factor_list.append(factor)
        ema_win = int(np.sqrt(ccc))
        
        factor1 = ema_1(self.factor_list[-ema_win * 3: ], ema_win * 3, 1 / (ema_win + 1))
        return factor1

    
    def pre_calculate(self, data):
        self.factor_list = []
        aaa = 50
        bbb = 225
        ccc = 20
        ddd = 10

        for i in range(50, -1, -1):
            if i == 0:
                dclose = data['close_secmain'][-100 * int(np.sqrt(aaa)):]
            else:
                dclose = data['close_secmain'][-100 * int(np.sqrt(aaa)) - i: -i]
                
            try:
                price_level = rolling_norm_raw(dclose, 100 * int(np.sqrt(aaa)))

                #price_level = rolling_norm(data['close'], 100 * int(np.sqrt(aaa))).fillna(method = 'ffill')
                price_std = nanstd_np(dclose[-bbb: ], ddof = 1)
                factor = (price_level / r(price_std))
                self.factor_list.append(factor)
            except:
                if len(factor_list) > 0:
                    self.factor_list.append(self.factor_list[-1])
                else:
                    self.factor_list.append(np.nan)
                        
