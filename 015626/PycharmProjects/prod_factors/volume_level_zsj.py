# -*- coding: utf-8 -*-
"""
author:       sujian zhi
fred:         minute
prod:         IC.CFE
factor_name:  fac
"""
import pandas as pd
import numpy as np
from factor_generator import FactorGenerator
from utils_zsj import *

"""
import inspect, os, sys
code_base = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
sys.path.insert(0, os.path.dirname(code_base))
from ts.factor.minute.utils_zsj import *
"""
class volume_level_zsj(FactorGenerator):
    def __init__(self):
        super(volume_level_zsj, self).__init__(factor_name = 'volume_level_zsj',
                                                required_columns = [ 'volume'],
                                                lookback_bars = 1400)

    def on_bar(self, data):
        ##### def data #####
        volume = data['volume']

        ##### calc factor #####
        ma_win = 60
        ts_pct_win = 1200
        volume_ma_raw = volume.rolling(ma_win).mean()
        volume_level = calc_ts_pct(volume_ma_raw, ts_pct_win)

        ##### format factor #####
        volume_level.name = self.__class__.__name__
        factor = pd.DataFrame(volume_level)
        return factor
