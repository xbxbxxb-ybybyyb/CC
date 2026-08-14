from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd


class PDPS_Hist2_120D(BaseFactor):
        factor_type = "DAY"
        depend_data = ["FactorData.Basic_factor.s_price_div_dps","FactorData.Basic_factor.is_valid_raw"]

        lag = 119

        def calc_single(self,database):
            factor = database.depend_data['FactorData.Basic_factor.s_price_div_dps']
            index_ = factor.index
            columns_ = factor.columns
            factor = factor.values
            is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw'].values
            factor = np.where(is_valid_raw==1,factor,np.nan)
            factor_mean = np.nanmean(factor,axis=0)
            factor_std = np.nanstd(factor,axis=0)
            factor = (factor[-1]-factor_mean)/factor_std
            factor[~np.isfinite(factor)] = np.nan

            return pd.Series(-factor,index=columns_)

