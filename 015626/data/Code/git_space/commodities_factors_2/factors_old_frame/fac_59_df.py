import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
import pandas as pd
from operators_cc import *
from utils_zsj import *

def ts_truncated_ema_1(data, d, alpha):
    # truncated ema
    if (alpha >= 1) or (alpha <= 0):
        raise ValueError('`alpha` must be in (0, 1)')
    weight = alpha * np.array([(1 - alpha) ** i for i in range(d)])[::-1]
    return ts_decay_linear(data=data, d=d, weight=weight)


def ts_truncated_ema_span_1(data, d, span):
    # truncated ema
    return ts_truncated_ema_1(data=data, d=d, alpha=2 / (span + 1))

#dop_ma_zsj_IF
class fac_59_df(FactorGenerator):
    def __init__(self):
        required_columns=['close', 'second_main_mask']

        super(fac_59_df, self).__init__(required_columns=required_columns
                                  )
        

    def on_bar(self, data, aa, bb, ccc):
        
        ##### def data #####
        close = data['close']
        mask = data['second_main_mask']
        vol = close.diff().rolling(10, min_periods = 1).std()[mask].mean(axis = 1)

        unit = int((mask.index[-1] - mask.index[-2]).total_seconds() / 60)

        aa = int(360 / unit)
        bb = int(25 / unit)
        ccc = 25
        
        ##### calc factor #####

        def calc_dpo_sig(close, roll_win, mask):
            dpo = close - REF(MA(close, roll_win), int(roll_win / 2 + 1))
            return dpo[mask].mean(axis = 1)

        factor_name = 'dpo_ma'
        dpo_win = aa
        ma_win = int(np.sqrt(bb))
        ts_pct_win = ccc
        
        dpo_raw = calc_dpo_sig(close, dpo_win, mask)
        dpo_ma_raw = ts_truncated_ema_1(dpo_raw, ma_win * 3, 1 / (ma_win + 1))
        dpo_ma = calc_ts_pct(dpo_ma_raw / r(np.sqrt(vol)), ts_pct_win)

        ##### format factor #####
        dpo_ma.name = self.__class__.__name__
        factor = pd.DataFrame(dpo_ma)

        return factor