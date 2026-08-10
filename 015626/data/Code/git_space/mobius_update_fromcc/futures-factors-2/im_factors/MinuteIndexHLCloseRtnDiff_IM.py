import numpy as np
from future_factor import FutureFactor

class MinuteIndexHLCloseRtnDiff_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = dict()
    data_dict['Stock'] = ['close']
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'

    def calculate(self, data):
        n = 15

        close = data['close'].values

        rtn = close[1:] / close[:-1] - 1

        mid_close = np.nanpercentile(close[-1], 50)
        rtn_mean = np.nanmean(rtn[-n:], axis=0)

        high_rtn = rtn_mean[close[-1] > mid_close]
        low_rtn = rtn_mean[close[-1] < mid_close]

        factor_value = np.nanmean(high_rtn) - np.nanmean(low_rtn)

        if np.isnan(factor_value) or np.isinf(factor_value):
            factor_value = 0

        return factor_value