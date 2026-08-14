import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class VolPriceRunner(BaseFactor):
    depend_data = ["FactorData.Basic_factor.amt", "FactorData.Basic_factor.free_float_shares",
                   "FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor"]
    lag = 40

    def calc_single(self, database):
        amt = database.depend_data['FactorData.Basic_factor.amt']
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        stk_code = amt.columns
        amt, ffs, close, adjfactor = amt.values, ffs.values, close.values, adjfactor.values
        amt, ffc, close = amt * 10000, ffs * close, close * adjfactor / adjfactor[-1]
        turn = amt / ffc
        ret = (close / np.roll(close, 1, axis=0) -1)[1:]
        turn_centered = np.nan * np.ones((20, turn.shape[1]))
        ret_centered = np.nan * np.ones((20, ret.shape[1]))
        for i in range(20):
            temp = np.roll(turn, i+1, axis=0)[-20:]
            turn_centered[-i-1] = temp[-1] - temp.mean(axis=0)
            temp = np.roll(ret, i, axis=0)[-20:]
            ret_centered[-i-1] = np.abs(temp[-1] - temp.mean(axis=0))
        turn_centered[np.isinf(turn_centered)] = np.nan
        ret_centered[np.isinf(ret_centered)] = np.nan
        corr = array_corr_np(turn_centered, ret_centered)
        corr[(np.isnan(turn_centered) | np.isnan(ret_centered)).sum(axis=0) > 0] = np.nan
        alpha = pd.Series(-corr, index=stk_code)
        return alpha
