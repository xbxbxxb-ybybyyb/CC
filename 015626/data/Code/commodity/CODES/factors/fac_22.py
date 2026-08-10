import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *


#dop_ma_zsj_IF
class fac_22(FactorGenerator):
    def __init__(self):
        required_columns=['close']

        super(fac_22, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        ##### def data #####
        close = data['close']

        ##### calc factor #####

        def calc_dpo_sig(close, roll_win):
            dpo = close - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo

        factor_name = 'dpo_ma'
        dpo_win = aa
        ma_win = int(np.sqrt(bb))
        ts_pct_win = ccc

        dpo_raw = calc_dpo_sig(close, dpo_win)
        dpo_ma_raw = dpo_raw.rolling(ma_win, 1).mean()
        dpo_ma = calc_ts_pct(dpo_ma_raw, ts_pct_win)

        ##### format factor #####
        dpo_ma.name = self.__class__.__name__
        factor = pd.DataFrame(dpo_ma)

        return factor