from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
import copy


class IlliqNeg60d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close_badj","FactorData.Basic_factor.amt",
    "FactorData.Basic_factor.is_valid"]

    lag = 59

    def calc_single(self,database):

        amt = database.depend_data['FactorData.Basic_factor.amt'].values
        close = database.depend_data['FactorData.Basic_factor.close_badj']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid'].values
        amt = np.where(is_valid==1,amt,np.nan)
        re= close.values/close.shift(1).values -1
        re[re >= 0] = np.nan
        illiq_neg = abs(re)/amt

        illiq_neg_ma = np.nanmean(illiq_neg,axis=0)
        illiq_neg_ma[~np.isfinite(illiq_neg_ma)] = np.nan

        return pd.Series(illiq_neg_ma,index=close.columns)

        