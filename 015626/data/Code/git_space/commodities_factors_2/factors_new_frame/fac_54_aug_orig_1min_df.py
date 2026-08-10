from rolling_adj import *

from operators_cc_com import *

from commodity_framework import FutureFactor

import numpy as np





def rolling_normalize_array(sig, window):
    if len(sig) < window:

        sig_max = move_max_bk(sig,window,min_count = int(window/2))

        sig_min = move_min_bk(sig,window,min_count = int(window/2))

    else:

        w2 = len(sig)

        sig_max = move_max_bk(sig,w2,min_count = int(w2/2))

        sig_min = move_min_bk(sig,w2,min_count = int(w2/2))

    sig_roll_norm = (sig - sig_min) / (sig_max - sig_min) * 2 - 1

    return sig_roll_norm


    

class fac_54_aug_orig_1min_df(FutureFactor):

    def __init__(self, ticker, freq = 1):

        super().__init__()

        self.required_columns = ['close','open','high','low']

        self.ticker = ticker

        self.freq = freq

        self.normalize_size = int(5 * self.bars_dict[ticker] / freq)

        self.normalize_type = 'ts_rank'

        self.days_past = int(freq) * 2

        

    def calculate(self, data):

        twap = (data['close'] + data['open'] + data['high'] + data['low']) / 4

        twap = twap[-250:]

        rtn = twap[1:]/twap[:-1]-1

        price_level = rolling_normalize_array(twap,240)

        price_std = move_std_bk(rtn, window = 60, min_count = 5, ddof = 1)

        price_std[abs(price_std) < 1e-8] = np.nan

        factor_org = price_level[-8:] / price_std[-8:]

        factor = nanmean_np(factor_org)

        return factor