from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighLowCorrMeanSharpeDiff_IM(FutureFactor):
    data_type = 'IndexStock'
    days_past = 1
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    normalize_size = 120
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        lb = 236
        adj = data['adjfactor'].values
        close = data['close'].values * adj / adj[-1]
        rtn = close[1:] / close[:-1] - 1
        rtn = np.concatenate((rtn[:236], rtn[237:]), axis=0)
        rtn = rtn[-lb:]
        nan_num = np.isnan(rtn).sum(axis=0)
        zero_num = (rtn == 0).sum(axis=0)
        rtn = rtn[:, (nan_num == 0) & (zero_num < (lb / 2))]
        corr = np.corrcoef(rtn.T)
        corr_mean = corr.mean(axis=0)
        corr_mean_median = np.median(corr_mean)
        rtn_mean = rtn.mean(axis=0)
        rtn_mean_high = rtn_mean[corr_mean > corr_mean_median]
        rtn_mean_low = rtn_mean[corr_mean < corr_mean_median]
        f = rtn_mean_high.mean() / rtn_mean_high.std() - rtn_mean_low.mean() / rtn_mean_low.std()
        return f
