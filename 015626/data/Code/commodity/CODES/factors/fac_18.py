import numpy as np
from factor_generator import FactorGenerator
from operators_wsc_1_0 import *
from operators_cc import *
import pandas as pd
import bottleneck as bk

def calc_ts_pct(ts,ts_pct_win=20,min_pct=0.9,force_range=False):
    min_win = int(min_pct*ts_pct_win)
    ts_pct_np = bk.move_rank(ts,ts_pct_win,min_win)
    if force_range:
        ts_pct_np = (ts_pct_np + 1)/2
    ts_pct = place_back_format(ts_pct_np,ts)
    return ts_pct

def place_back_format(dat_mat,dat_orig):
    if isinstance(dat_orig,pd.DataFrame):
        dat_fmt = pd.DataFrame(dat_mat,index=dat_orig.index,columns=dat_orig.columns)
    elif isinstance(dat_orig,pd.Series):
        dat_fmt = pd.Series(dat_mat,index=dat_orig.index)
        dat_fmt.name = dat_orig.name
    else:
        dat_fmt = dat_mat
    return dat_fmt

# amihund_measure_zsj
class fac_18(FactorGenerator):
    def __init__(self):
        required_columns=['amount', 'close']

        super(fac_18, self).__init__(required_columns=required_columns
                                  )
        
    
    def on_bar(self, data, aa, bb, ccc):
        ##### def data #####
        close = data['close']
        amount = data['amount']
        minute_ret = close - close.shift(1)

        ##### calc factor #####
        ret_pos = minute_ret > 0
        amount = amount.replace({0: np.nan})
        amihund_measure_raw = minute_ret / amount

        min_pct = 0.9
        amihund_win = aa
        ts_pct_win = ccc * 300
        amihund_measure_raw_ma = amihund_measure_raw.rolling(amihund_win, int(amihund_win * min_pct)).mean()
        amihund_measure_raw_ma = amihund_measure_raw_ma.rolling(bb, min_periods = 1).mean()
        amihund_measure = calc_ts_pct(amihund_measure_raw_ma, ts_pct_win)
        amihund_measure.name = self.__class__.__name__
        ##### format factor #####
        factor = pd.DataFrame(amihund_measure)
        return factor
