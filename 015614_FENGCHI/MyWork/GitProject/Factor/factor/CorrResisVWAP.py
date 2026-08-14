from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import xfactor.Util as Util
import numpy as np
import pandas as pd


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class CorrResisVWAP(BaseFactor):
    factor_type = 'FIX'
    depend_data = ['FactorData.Basic_factor.high_adj_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.volume_adj_minute']
    lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        # stk_code = high.columns
        
        high = high.resample('5min').mean().dropna(how='all')
        high_ratio = high.values / np.nansum(high.values, axis=0)
        amt = amt.resample('5min').mean().dropna(how='all')
        amt_ratio = amt.values / np.nansum(amt.values, axis=0)
        vol = vol.resample('5min').mean().dropna(how='all')
        vol_ratio = vol.values / np.nansum(vol.values, axis=0)

        resis = pd.DataFrame(vol_ratio * high_ratio - amt_ratio,index=vol.index,columns=vol.columns)
        vwap = pd.DataFrame(amt_ratio / vol_ratio,index=vol.index,columns=vol.columns)

        result = -Util.array_coef(resis, vwap)

        return result
