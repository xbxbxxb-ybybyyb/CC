from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util

class RankPBDev(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.s_val_pb_new","FactorData.Basic_factor.sw_indcode1",
    "FactorData.Basic_factor.is_valid_raw"]

    lag = 5


    def calc_single(self,database):
        s_val_pb_new = database.depend_data['FactorData.Basic_factor.s_val_pb_new']
        is_valid_raw = database.depend_data['FactorData.Basic_factor.is_valid_raw'].values
        sw_indcode1 = database.depend_data['FactorData.Basic_factor.sw_indcode1'].values

        factor = np.where(is_valid_raw==1,s_val_pb_new.values,np.nan)
        industry_code = np.unique(sw_indcode1.flatten().astype(str)).tolist()
        if 'nan' in industry_code:
            industry_code.remove('nan')
        factor_rank = np.zeros([factor.shape[0],factor.shape[1]])
        
        for ind in industry_code:
            df = np.where(sw_indcode1==ind,factor,np.nan)
            df = pd.DataFrame(df,index=s_val_pb_new.index,columns=s_val_pb_new.columns)
            factor_rank = factor_rank+df.rank(axis=1,ascending=True,pct=True).fillna(0.).values
        factor_rank = np.where(~np.isnan(factor),factor_rank,np.nan)
        factor_rank = (factor_rank[-1]-np.nanmean(factor_rank,axis=0))/np.nanstd(factor_rank,axis=0)
        factor_rank[np.isinf(factor_rank)] = np.nan
        factor_rank[is_valid_raw[-1]==0] = np.nan

        return -pd.Series(factor_rank,index=s_val_pb_new.columns)