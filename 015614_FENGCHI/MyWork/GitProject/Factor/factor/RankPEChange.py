from xfactor.BaseFactor import BaseFactor
import pandas as pd
import numpy as np

class RankPEChange(BaseFactor):
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.pe_ttm",  "FactorData.Basic_factor.sw_indcode1", "FactorData.Basic_factor.is_valid"]
    reform_window = 21

    def calc_single(self, database):
        pe_ttm = database.depend_data['FactorData.Basic_factor.pe_ttm']
        industry_code = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']

        industry_code_date = industry_code.iloc[-1]
        industry_list = np.unique(industry_code_date.dropna().values).tolist()
        ans = pd.Series(0., index=pe_ttm.columns)
        for industry in industry_list:
            stocks = industry_code_date[industry_code_date==industry].index
            ans.loc[stocks] = pe_ttm.iloc[-1].loc[stocks].rank(ascending=True, pct=True).fillna(0.)
        ans[is_valid.iloc[-1]==0] = np.nan
        ans[~np.isfinite(ans)] = np.nan
        return ans

    def reform(self, temp_result):
        return 1. - temp_result / temp_result.shift(self.reform_window-1)



