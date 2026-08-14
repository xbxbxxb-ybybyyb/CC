from xfactor.BaseFactor import BaseFactor
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteCloseTurnRSharpe(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop", "merge"])        
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        amt = database.depend_data['FactorData.Basic_factor.amt_minute']

        t = amt.values
        c = close.values
        t_ma = np.nanmean(t[-5:], axis=0) / np.nanmean(t[-60:], axis=0)
        c_ma = np.nanmean(c[-5:], axis=0) / np.nanmean(c[-60:], axis=0)
        t_ma_rank = pd.Series(t_ma, index=close.columns).rank(ascending=False, pct=True)
        c_ma_rank = pd.Series(c_ma, index=close.columns).rank(ascending=False, pct=True)
        ans = t_ma_rank.values + c_ma_rank.values
        ans = pd.Series(ans, index=close.columns)
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window, 1).mean() / temp_result.rolling(self.reform_window, 1).std()