# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import numpy as np
from xfactor.FixUtil import minute_data_transform


def array_corr_np(x, y):
    x[np.isnan(x) | np.isnan(y)] = np.nan
    y[np.isnan(x) | np.isnan(y)] = np.nan
    d_x, d_y = x - np.nanmean(x, axis=0), y - np.nanmean(y, axis=0)
    numerator = np.nanmean(d_x * d_y, axis=0)
    denominator = np.nanstd(x, axis=0) * np.nanstd(y, axis=0)
    corr = numerator / denominator
    corr[np.isinf(corr)] = np.nan
    return corr


class FR20d_1130(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.turn",
                   "FactorData.Basic_factor.pre_close"]
    lag = 1
    reform_window = 20
    re_abs_temp = []
    turn_temp = []

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        close = database.depend_data["FactorData.Basic_factor.close_minute"]
        turn = database.depend_data["FactorData.Basic_factor.turn"]
        pre_close = database.depend_data["FactorData.Basic_factor.pre_close"]
        stk_code = close.columns
        re = close.values[-240:][119] / pre_close.values[-1] - 1
        turn = np.where(re < 0, turn.values[-2], np.nan)
        self.re_abs_temp.append(np.abs(re))
        self.turn_temp.append(turn)
        self.re_abs_temp = self.re_abs_temp[-20:]
        self.turn_temp = self.turn_temp[-20:]
        if (len(self.re_abs_temp) == 20) & (len(self.turn_temp) == 20):
            re_abs_temp = np.array(self.re_abs_temp)
            turn_temp = np.array(self.turn_temp)
            factor = pd.Series(-array_corr_np(re_abs_temp, turn_temp), index=stk_code)
        else:
            factor = pd.Series(np.nan, index=stk_code)
        # factor = pd.Series(-array_corr_np(np.abs(re[-20:]), turn_former[-20:]), index=stk_code)
        return factor
