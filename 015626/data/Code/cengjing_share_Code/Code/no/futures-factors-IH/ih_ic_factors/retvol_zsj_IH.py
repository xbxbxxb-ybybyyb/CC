import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class retvol_zsj_IH(FutureFactor):
    data_type = 'Future'
    days_past = 2
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IH':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IH'].values[-302:]
        future_ret = ts_pct_change(future_close, 1)
        retvol_raw = bk.move_std(future_ret, 60, 1)
        retvol = bk.move_rank(retvol_raw, 240, int(240*0.9))
        return retvol[-1]

