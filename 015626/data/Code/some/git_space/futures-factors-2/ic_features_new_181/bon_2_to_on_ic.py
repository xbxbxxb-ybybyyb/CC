import numpy as np
import pandas as pd
from future_factor import FutureFactor


class bon_2_to_on_ic(FutureFactor):
    data_type = 'IndexStock'
    instrument_type = 'recent'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['buy_big_lo_counts', 'sell_big_lo_counts', 'buy_lo_counts', 'sell_lo_counts']
    normalize_size = 1
    normalize_type = 'rolling_norm'

    def calculate(self, data):
        buy_big_lo_counts = data['buy_big_lo_counts'].values[-1]
        sell_big_lo_counts = data['sell_big_lo_counts'].values[-1]
        buy_lo_counts = data['buy_lo_counts'].values[-1]
        sell_lo_counts = data['sell_lo_counts'].values[-1]

        # 为了处理极值，做截断处理
        buy_big_lo_counts[buy_big_lo_counts > 2000] = 2000
        sell_big_lo_counts[sell_big_lo_counts > 500] = 500
        buy_lo_counts[buy_lo_counts > 20000] = 20000
        sell_lo_counts[sell_lo_counts > 10000] = 10000

        factor = np.nansum(buy_big_lo_counts + sell_big_lo_counts) / np.nansum(buy_lo_counts + sell_lo_counts)
        return factor
