import numpy as np
from xfactor.BaseFactor import BaseFactor

class VwapCloseAdj20d(BaseFactor):
    # def __init__(self,json_path):
    #     super(VwapCloseAdj20d,self).__init__(json_path)

    # def definition(self,vwap_adj,close_adj,is_valid_raw,n=20):
    #     vwap_adj_valid=vwap_adj[is_valid_raw==1]
    #     close_adj_valid=close_adj[is_valid_raw==1]
    #     # vwap_20 = recent_rolling(amt, n, 'sum')/recent_rolling(volume, n, 'sum')
    #     vwap_20 = vwap_adj_valid.rolling(window=n, min_periods=int(n * 0.8)).mean()
    #     vwap_20_minus_close = vwap_20 - close_adj_valid
    #     vwap_20_add_close = vwap_20 + close_adj_valid
    #     result = vwap_20_minus_close.rank(axis=1) / vwap_20_add_close.rank(axis=1)
    #     result[~np.isfinite(result)] = np.nan

    #     return result

    factor_type = "DAY"

    s_vwap = 'FactorData.Basic_factor.vwap'
    s_close = 'FactorData.Basic_factor.close'
    s_adjfactor = 'FactorData.Basic_factor.adjfactor'

    depend_data = [s_vwap, s_close, s_adjfactor]

    n = 20

    lag = n-1

    def calc_single(self, database):
        vwap = database.depend_data[self.s_vwap]
        close = database.depend_data[self.s_close]
        adjfactor = database.depend_data[self.s_adjfactor]

        close_adj = close * adjfactor
        vwap_adj = vwap * adjfactor

        vwap_20 = vwap_adj.rolling(window=self.n, min_periods=int(self.n * 0.8)).mean()
        vwap_20_minus_close = vwap_20 - close_adj
        vwap_20_add_close = vwap_20 + close_adj
        result = vwap_20_minus_close.rank(axis=1) / vwap_20_add_close.rank(axis=1)

        result[~np.isfinite(result)] = np.nan

        # vwap_20 = vwap.tail(self.n).mean(axis=0, skipna=True).iloc[-1]
        # vwap_20_minus_close  = vwap_20 - close
        # vwap_20_add_close = vwap_20 + close
        # res = vwap_20_minus_close.rank() / vwap_20_add_close.rank()
        return result.iloc[-1]
    
    # def reform(self, temp_result):
    #     temp_result[~np.isfinite(temp_result)] = np.nan
    #     return temp_result


    

