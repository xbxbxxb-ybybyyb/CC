import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *
from operators_all_wsc import cross_hub_num

# vma_std
class fac_44_orig_1min_df(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'open', 'second_main_mask']

        super(fac_44_orig_1min_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        ##### def data #####
        aaa = 60
        bbb = 240
        ccc = 5
        mask = data['second_main_mask']
        close = data['close']
        high = data['high']
        low = data['low']
        ts_open = data['open']

        def calc_vma(high, low, ts_open, close, roll_win=20, mask = mask):
            price = (high + low + ts_open + close) / 4
            vma = price.rolling(roll_win, min_periods = 1).mean()
            vma_diff = close.rolling(5, min_periods = 1).mean() - vma
            return vma_diff[mask].mean(axis = 1)

        factor_name = 'vma_std'
        roll_win = aaa
        std_win = int(np.sqrt(bbb))
        ts_pct_win = 300 * ccc
        score = calc_vma(high, low, ts_open, close, roll_win)
        co = (cross_hub_num(data['close'], 120)[mask].mean(axis = 1) / 5) + 1
        score = score.rolling(std_win, min_periods = 1).mean() / r(co)
        vma_std = ts_rank(score, ts_pct_win)

        ##### format factor #####
        vma_std.name = self.__class__.__name__
        factor = pd.DataFrame(vma_std)
        return factor
