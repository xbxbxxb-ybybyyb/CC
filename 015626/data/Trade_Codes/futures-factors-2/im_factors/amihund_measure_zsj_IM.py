from future_factor import FutureFactor
import numpy as np
import bottleneck as bk
import pandas as pd

class amihund_measure_zsj_IM(FutureFactor):
    data_type = 'Future' 
    instrument_type = 'recent'
    days_past = 6
    data_dict = dict()
    data_dict['Index_Id'] = {'000852.SH':['close','amount']}
    normalize_size = 0
    normalize_type = 'rolling_norm' # normalize方法'rolling_norm'或者'ts_rank'
    num_range = None
    handle_preadj = None 

    def calculate(self, data):
        close = data['close_000852.SH'][-1290:]
        amount = data['amount_000852.SH'][-1290:]
        minute_ret = close / close.shift(1) - 1

        ret_pos = minute_ret > 0
        amount = amount.replace({0: np.nan})
        amihund_measure_raw = minute_ret / amount

        amihund_measure_raw_ma = bk.move_mean(amihund_measure_raw, 90, 81, axis = 0)
        factor = bk.move_rank(amihund_measure_raw_ma, 1200, 1080, axis = 0)[-1]
        return factor
