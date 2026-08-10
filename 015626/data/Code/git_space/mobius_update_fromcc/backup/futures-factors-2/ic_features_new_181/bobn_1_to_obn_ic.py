import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bobn_1_to_obn_ic(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_super_lo_counts', 'buy_lo_counts']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, data):
        buy_super_lo_counts = data['buy_super_lo_counts'].values[-1]
        buy_lo_counts = data['buy_lo_counts'].values[-1]

        # 为了处理极值，做截断处理
        buy_super_lo_counts[buy_super_lo_counts > 200] = 200
        buy_lo_counts[buy_lo_counts > 20000] = 20000

        factor = np.nansum(buy_super_lo_counts) / np.nansum(buy_lo_counts)
        return factor
