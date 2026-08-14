import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform


class MinuteTTLSStdRank(BaseFactor):
    depend_data = ['FactorData.Basic_factor.close_adj_minute', 'FactorData.Basic_factor.amt_minute']
    lag = 4

    def calc_single(self, database):
        minute_data_transform(database.depend_data, ['drop', 'merge'])
        close = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']
        stk_code = close.columns
        close, amt = close.values, amt.values
        factor = np.nan * np.ones((5, len(stk_code)))
        for i in range(5):
            close_temp = close[-(i+1)*240:][:240]
            amt_temp = amt[-(i+1)*240:][:240]
            ret = close_temp[1:] / close_temp[:-1] - 1
            amt_std_long = np.nanstd(np.where(ret > 0, amt_temp[1:], np.nan)[-30:], axis=0)
            amt_std_short = np.nanstd(np.where(ret < 0, amt_temp[1:], np.nan)[-30:], axis=0)
            factor[-(i+1)] = (5-i) * pd.Series(amt_std_short / amt_std_long).rank().values
        result = pd.Series(np.nanmean(factor, axis=0), index=stk_code)
        return result

