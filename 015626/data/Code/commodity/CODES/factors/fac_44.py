import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *


# vma_std
class fac_44(FactorGenerator):
    def __init__(self):
        required_columns=['low', 'high', 'close', 'open']

        super(fac_44, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aaa, bbb, ccc):
        ##### def data #####
        close = data['close']
        high = data['high']
        low = data['low']
        ts_open = data['open']

        def calc_vma(high, low, ts_open, close, roll_win=20):
            price = (high + low + ts_open + close) / 4
            vma = MA(price, roll_win)
            vma_diff = close - vma
            return vma_diff

        factor_name = 'vma_std'
        roll_win = aaa
        std_win = bbb
        ts_pct_win = 300 * ccc
        score = calc_vma(high, low, ts_open, close, roll_win)
        score = score.ewm(std_win, min_periods = 1).mean()
        vma_std = ts_rank(score, ts_pct_win)

        ##### format factor #####
        vma_std.name = self.__class__.__name__
        factor = pd.DataFrame(vma_std)
        return factor
