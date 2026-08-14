from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd


class EP_Hist2_120D(BaseFactor):

        factor_type = "DAY"
        depend_data = ["FactorData.Basic_factor.pe_ttm","FactorData.Basic_factor.is_valid_raw"]

        lag = 119

        def calc_single(self,database):
            pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
            is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw'].values
            columns_ = pe_ttm.columns
            
            pe_ttm = np.where(is_valid_raw==1,pe_ttm.values,np.nan)
            factor = 1/pe_ttm 
            factor_mean = np.nanmean(factor,axis=0)
            factor_std = np.nanstd(factor,axis=0)
            factor = (factor[-1]-factor_mean)/factor_std
            factor[~np.isfinite(factor)] = np.nan
            return pd.Series(factor,index=columns_)
            
