from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class MinVVM(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.volume_adj_minute",
                   "FactorData.Basic_factor.amt_minute",
                   "FactorData.Basic_factor.is_valid", ]

    lag = 0
    minute_lag = 0
    reform_window = 20

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["merge", "merge"])
        amt_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_adj_minute = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values == 1, index=is_valid.index, columns=is_valid.columns).iloc[-1]

        vwap_adj = (amt_minute / volume_adj_minute)
        vwap_adj[np.isinf(vwap_adj)] = np.nan
        vwap_adj = vwap_adj.fillna(method='ffill')
        volume = volume_adj_minute.fillna(0)

        vwap_adj_avg = vwap_adj.mean()
        vwap_adj_weightavg = (vwap_adj * volume).sum() / volume.sum()

        result = np.log(vwap_adj_avg / vwap_adj_weightavg)

        return result[valid]

    def reform(self, temp_result):
        res = temp_result.rolling(5, 1).mean()
        res = res.rolling(10, 1).min()
        return res



