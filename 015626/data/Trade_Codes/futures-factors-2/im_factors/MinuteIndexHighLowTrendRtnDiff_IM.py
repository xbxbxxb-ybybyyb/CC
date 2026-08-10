from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowTrendRtnDiff_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'high', 'low', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 60
        adj = data['adjfactor'].values[-lb:]
        high = data['high'].values[-lb:] * adj / adj[-1]
        low = data['low'].values[-lb:] * adj / adj[-1]
        close = data['close'].values[-lb:] * adj / adj[-1]
        nan_num = np.isnan(high).sum(axis=0) + np.isnan(low).sum(axis=0) + np.isnan(close).sum(axis=0)
        high = high[:, nan_num == 0]
        low = low[:, nan_num == 0]
        close = close[:, nan_num == 0]
        mdd = -np.min(close / np.maximum.accumulate(high, axis=0) - 1, axis=0)
        mbb = np.max(close / np.minimum.accumulate(low, axis=0) - 1, axis=0)
        trend = np.minimum(mdd, mbb)
        trend = np.where(trend == 0, np.nan, trend)
        median = np.nanmedian(trend)
        rtn = close[-1] / close[0] - 1
        f = (rtn[trend > median].mean() - rtn[trend < median].mean()) / np.nanstd(rtn)
        return f
