import bottleneck as bk
from future_factor import FutureFactor
from operators_wsc_1_0 import *



class ma_displaced_std_zsj(FutureFactor):
    data_type = 'Future'
    days_past = 6
    data_dict = dict()
    instrument_type = 'recent'
    # data_dict['Index_Id'] = {'000905.SH':['close']}
    data_dict['Continuous_Data'] = {'IC':['close']}
    normalize_size = 1
    normalize_type = 'ts_rank'
    num_range = None
    
    def calculate(self, data):
        future_close = data['close_cont_IC'].values[-1351:]
        ma_close = bk.move_mean(future_close, 90, 1)
        ma_displaced = ts_delay(ma_close, 10)
        ma_diff = future_close - ma_displaced
        score_raw = bk.move_std(ma_diff, 40, 36)
        ma_displaced_std = bk.move_rank(score_raw, 1210, int(1210*0.9))
        return ma_displaced_std[-1]
