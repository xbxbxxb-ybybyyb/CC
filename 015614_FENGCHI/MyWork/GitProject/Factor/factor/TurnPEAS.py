import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class TurnPEAS(BaseFactor):
    depend_data = ['FactorData.Basic_factor.pe_ttm', 'FactorData.Basic_factor.amt',
                   'FactorData.Basic_factor.free_float_shares', 'FactorData.Basic_factor.close',
                   'FactorData.Basic_factor.sw_indcode1', 'FactorData.Basic_factor.is_valid_raw']
    reform_window = 5

    def calc_single(self, database):
        pe = database.depend_data['FactorData.Basic_factor.pe_ttm']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        ffs = database.depend_data['FactorData.Basic_factor.free_float_shares']
        close = database.depend_data['FactorData.Basic_factor.close']
        ind = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        valid = database.depend_data['FactorData.Basic_factor.is_valid_raw']
        stk_code = pe.columns
        ffc = ffs.values[-1] * close.values[-1]
        alpha_temp = pe.values[-1] * (amt.values[-1] / ffc)
        alpha_temp[valid.values[-1] != 1] = np.nan
        alpha_temp = pd.Series(alpha_temp, index=stk_code)
        ind = ind.iloc[-1]
        ind_mean = ind.map(alpha_temp.groupby(ind).mean())
        alpha_temp = alpha_temp.values / ind_mean.values
        alpha = pd.Series(-(alpha_temp - np.nanmean(alpha_temp)) / np.nanstd(alpha_temp), index=stk_code)
        return alpha

    def reform(self, temp_result):
        alpha = temp_result.rolling(5).mean() / temp_result.rolling(5).std()
        return alpha
