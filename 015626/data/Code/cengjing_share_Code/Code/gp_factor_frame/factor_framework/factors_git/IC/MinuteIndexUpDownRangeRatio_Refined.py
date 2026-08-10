from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownRangeRatio_Refined(FutureFactor):
    '''
    Description: cs_mean(ts_mean(where(rtn > 0, hml, nan), 30) / ts_mean(where(rtn < 0, hml, nan), 30)),
                 rtn = pct_chg(close * adjfactor, 1),
                 hml = high * adjfactor - low * adjfactor.
    Class: MTM
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'high', 'low', 'adjfactor']
    normalize_size = 20 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-31:]
        close[close == 0] = np.nan
        high = data['high'].values[-30:]
        high[high == 0] = np.nan
        low = data['low'].values[-30:]
        low[low == 0] = np.nan
        adj = data['adjfactor'].values[-31:]
        close = close * adj
        high = high * adj[-30:]
        low = low * adj[-30:]
        rtn = np.diff(close, axis=0) / close[:-1]
        hml = high - low
        ratio = np.nanmean(np.where(rtn > 0, hml, np.nan), axis=0) / np.nanmean(np.where(rtn < 0, hml, np.nan), axis=0)
        ratio[np.isinf(ratio)] = np.nan
        f = np.nanmean(ratio)
        return f
