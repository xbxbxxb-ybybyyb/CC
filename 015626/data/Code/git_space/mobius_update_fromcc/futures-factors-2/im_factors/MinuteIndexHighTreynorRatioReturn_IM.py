from future_factor import FutureFactor
import numpy as np


class MinuteIndexHighTreynorRatioReturn_IM(FutureFactor):
    '''
    Description: cs_mean(ts_mean(rtn_high, from 09:30 T-5)),
                 rtn_high = rtn[:, TreynorRatio > percentile(TreynorRatio, 90)],
                 TreynorRatio = alpha / beta,
                 alpha = ts_mean(rtn, from 09:30 T-5) - ts_mean(rtn_000905.SH, ffrom 09:30 T-5),
                 beta = cov(rtn, rtn_000905.SH) / var(rtn_000905.SH),
                 rtn = pct_chg(close * adjfactor, 1),
                 rtn_000905.SH = pct_chg(close_000905.SH, 1).
    Class: Return_Risk
    Author: jinpx, modified by hefj
    '''
    data_type = 'IndexStock'
    days_past = 5
    data_dict = {}
    data_dict['Stock'] = ['close', 'adjfactor']
    data_dict['Index_Id'] = {'000852.SH': ['close']}
    normalize_size = 1 * 237
    normalize_type = 'ts_rank'
    
    def calculate(self, data):
        idx = data['close'].index
        close = data['close'].values
        close[close == 0] = np.nan
        adj = data['adjfactor'].values
        adj[adj == 0] = np.nan
        index_close = data['close_000852.SH'].reindex(index=idx).values
        close = close * adj
        rtn = np.diff(close, axis=0) / close[:-1]
        index_rtn = np.diff(index_close, axis=0) / index_close[:-1]
        beta = ((rtn - np.mean(rtn, axis=0)) * (index_rtn - np.mean(index_rtn))).mean(axis=0) / np.var(index_rtn)
        beta[beta < 0] = np.nan
        rtn_mean = np.nanmean(rtn, axis=0)
        index_rtn_mean = np.nanmean(index_rtn)
        tr = (rtn_mean - index_rtn_mean) / beta
        f = np.nanmean(rtn_mean[tr > np.percentile(tr[~np.isnan(tr)], 90)])
        return f
