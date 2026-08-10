from future_factor import FutureFactor
import numpy as np


class MinuteIndexUpDownSpreadRatio(FutureFactor):
    '''
    Description: ts_mean(ts_mean(where(rtn_cs_mean > 0, spread_cs_mean, nan), 40) / ts_mean(where(rtn_cs_mean < 0, spread_cs_mean, nan), 40), 10),
                 rtn_cs_mean = cs_mean(pct_chg(close * adjfactor, 1)),
                 spread_cs_mean = cs_mean(AskP0 - BidP0).
    Class: Bid_Ask
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'BidP0', 'AskP0', 'adjfactor']
    normalize_size = 10 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        close = data['close'].values[-51:]
        close[close == 0] = np.nan
        bid = data['BidP0'].values[-50:]
        bid[bid == 0] = np.nan
        ask = data['AskP0'].values[-50:]
        ask[ask == 0] = np.nan
        adj = data['adjfactor'].values[-51:]
        adj[adj == 0] = np.nan
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        spread = ask - bid
        ratio = []
        for j in range(1, 11):
            r = np.nanmean(rtn[-(40 + j): -j], axis=1)
            s = np.nanmean(spread[-(40 + j): -j], axis=1)
            ratio.append(np.nanmean(s[r > 0]) / np.nanmean(s[r < 0]))
        f = np.nanmean(ratio)
        return f
