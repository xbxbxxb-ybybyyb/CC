import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

# pos_ma_long
class fac_35(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_35, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        ##### def data #####
        close = data['close']

        ##### calc factor #####
        def calc_pos(close, roll_win=100):
            price = (close - REF(close, roll_win)) / REF(close, roll_win)
            pos = (price - MIN(price, roll_win)) / (MAX(price, roll_win) - MIN(price, roll_win))
            return pos

        """pos_ma_long"""
        factor_name = 'pos_ma_long'
        roll_win = aa
        ma_win = int(np.sqrt(bb))
        ts_pct_win = ccc * 300
        score_raw = calc_pos(close, roll_win)
        pos_ma_long = calc_ma_helper(score_raw, ma_win, ts_pct_win)

        ##### format factor #####
        pos_ma_long.name = self.__class__.__name__
        factor = pd.DataFrame(pos_ma_long)
        # factor[factor>=0.5] = np.nan
        return factor