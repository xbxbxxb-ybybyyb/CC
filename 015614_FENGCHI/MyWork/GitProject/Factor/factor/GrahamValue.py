from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class GrahamValue(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj","FactorData.Basic_factor.is_valid","FactorData.Basic_factor.net_assets_today",
    "FactorData.Basic_factor.free_float_shares","FactorData.Basic_factor.pe_ttm","FactorData.Basic_factor.total_shares"]

    lag = 20

    def calc_single(self,database):
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid'].values
        close_adj = database.depend_data['FactorData.Basic_factor.close_badj']
        close = close_adj.values
        net_assets_today = database.depend_data['FactorData.Basic_factor.net_assets_today'].values
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares'].values
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm'].values
        total_shares = database.depend_data['FactorData.Basic_factor.total_shares'].values

        eps_fake = total_shares*close/pe_ttm/free_float_shares
        nps_fake = net_assets_today/free_float_shares/10000.
        price_fake = pd.DataFrame(np.sqrt(eps_fake*nps_fake),index=close_adj.index,columns=close_adj.columns)

        price_fake_rank = price_fake.rank(pct=True,axis=1).values
        close_adj_rank = close_adj.rank(pct=True,axis=1).values

        factor =  pd.DataFrame((price_fake_rank - close_adj_rank)/(1+close_adj_rank),index=close_adj.index,columns=close_adj.columns)
        factorM = ((factor.values - factor.rolling(window=self.lag).mean().values)/factor.rolling(window=self.lag).std().values)
        factorM[np.isinf(factorM)]=0
        factorM[is_valid==0] = np.nan 

        return pd.Series(factorM[-1],index=close_adj.columns)
