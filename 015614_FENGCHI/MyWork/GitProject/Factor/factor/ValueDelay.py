from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class ValueDelay(BaseFactor): 
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor", "FactorData.Basic_factor.net_assets_today",
                   "FactorData.Basic_factor.free_float_shares", "FactorData.Basic_factor.pe_ttm", "FactorData.Basic_factor.total_shares",
                   "FactorData.Basic_factor.is_valid"]
    lag = 80
    reform_window = 80

    def calc_single(self, database):
        close = database.depend_data['FactorData.Basic_factor.close']
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor'] 
        net_assets_today = database.depend_data['FactorData.Basic_factor.net_assets_today'] 
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
        total_shares = database.depend_data['FactorData.Basic_factor.total_shares']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        close_adj = close.values * adjfactor.values
        eps_fake = total_shares.values * adjfactor.values / pe_ttm.values / free_float_shares.values
        nps_fake = net_assets_today.values / (free_float_shares.values * close.values * 10000.)
        price_fake = np.sqrt(eps_fake*nps_fake)

        close_adj_rank_delay = pd.Series(close_adj[-1-self.lag], index=close.columns).rank(pct=True)
        price_fake_rank = pd.Series(price_fake[-1], index=close.columns).rank(pct=True)        
        ans =  (price_fake_rank.values - close_adj_rank_delay.values) / (1. + close_adj_rank_delay.values)

        ans = pd.Series(ans, index=close.columns)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        alpha = (temp_result - temp_result.rolling(self.reform_window).mean() ) / temp_result.rolling(self.reform_window).std()
        return alpha