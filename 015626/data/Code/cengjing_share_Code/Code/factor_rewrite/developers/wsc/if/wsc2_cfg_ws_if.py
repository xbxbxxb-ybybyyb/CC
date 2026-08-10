import numpy as np
from future_factor import FutureFactor
from operators_wsc_1_0 import *


class wsc2_cfg_ws_if(FactorGeneratorComplex):
class wsc2_cfg_ws_if(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    instrument_type = None
    data_dict['Stock'] = ['weight', 'close', 'open', 'volume']
    normalize_size = 1200
    normalize_type = 'ts_rank'
    num_range = '(-0.5,1]'
    handle_preadj = True
    
    def calculate(self, data):
        stk_weight = data['weight'].values[-51:]
        stk_close = data['close_preadj'].values[-51:]
        stk_open = data['open_preadj'].values[-51:]
        stk_volume = data['volume_preadj'].values[-51:]
        factor_init = (stk_close - ts_delay(stk_open, 30)) * stk_volume
        factor_raw = np.nansum(factor_init * stk_weight, axis=1)
        factor_mean = ts_mean(factor_raw, 20)
        return factor_mean[-1]
