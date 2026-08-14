import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteCloseTurnSharp(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.free_float_shares', 'FactorData.Basic_factor.close']
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close_min = database.depend_data['FactorData.Basic_factor.close_minute']
        amt_min = database.depend_data['FactorData.Basic_factor.amt_minute']
        close = database.depend_data['FactorData.Basic_factor.close']
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares']
        stk_code = close_min.columns.union(ffs.columns)
        close_min = close_min.reindex(columns=stk_code)
        amt_min = amt_min.reindex(columns=stk_code)
        close = close.reindex(columns=stk_code)
        ffs = ffs.reindex(columns=stk_code)
        ffc = ffs.values[-1] * 10000 * close.values[-1]
        liq = np.nansum(amt_min.values[-15:], axis=0) / ffc
        c_ma = np.nansum(close_min.values[-5:], axis=0) / np.nansum(close_min.values[-30:], axis=0)
        liq_rank = pd.Series(liq).rank(ascending=False, pct=True).values
        c_ma_rank = pd.Series(c_ma).rank(ascending=False, pct=True).values
        result = pd.Series(liq_rank + c_ma_rank, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(5, min_periods=1).mean() / temp_result.rolling(5, min_periods=1).std()
        return alpha
