import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


def rolling_ewm(df, n):
    seq = [(1 - (2.0 / (n + 1))) ** (n - i) for i in range(1, n + 1)]
    weight = np.array(seq)
    return df.rolling(n).apply(lambda x: np.nansum(x * weight) / max(weight[np.isnan(x)].sum(), 1. / n))


class hfMktLSCapMR5(BaseFactor):
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                   'FactorData.Basic_factor.volume_minute', 'FactorData.Basic_factor.amt_minute']
    lag = 1
    reform_window = 5
    factor_type = 'FIX'

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        high = database.depend_data['FactorData.Basic_factor.high_minute']
        low = database.depend_data['FactorData.Basic_factor.low_minute']
        vol = database.depend_data['FactorData.Basic_factor.volume_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = high.columns
        high, low, vol, amt = high.values[-240:], low.values[-240:], vol.values[-240:], amt.values[-240:]
        vwap = amt / vol
        vwap_last = np.roll(vwap, 1, axis=0)
        vwap_last[0] = np.nan
        rs_flag = vwap > vwap_last
        high_cap = high * vol
        low_cap = low * vol
        part_0 = np.nanmean(np.where(rs_flag, high_cap - amt, np.nan), axis=0)
        part_1 = np.nanmean(np.where(~rs_flag, amt - low_cap, np.nan), axis=0)
        result = part_0 / part_1
        result[np.isinf(result)] = np.nan
        result = pd.Series(-result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -rolling_ewm(temp_result, 5)
        alpha[alpha.isnull().all(axis=1)] = 0
        return alpha
