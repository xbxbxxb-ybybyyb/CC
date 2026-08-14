import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor


class RelativeIndPEGAvg(BaseFactor):
    depend_data = ["FactorData.Basic_factor.pe_ttm", "FactorData.Basic_factor.sw_indcode1"]
    reform_window = 20

    def calc_single(self, database):
        pe = database.depend_data['FactorData.Basic_factor.pe_ttm']
        indcode = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        stk_code = pe.columns
        pe, indcode = pe.iloc[-1], indcode.iloc[-1]
        pe_norm = (pe - pe.min()) / (pe.max() - pe.min())
        relative_pe = pe / indcode.map(pe.groupby(indcode).mean())
        relative_pe_norm = (relative_pe - relative_pe.min()) / (relative_pe.max() - relative_pe.min())
        result = (pe_norm * relative_pe_norm).values ** 0.5
        result = pd.Series(result, index=stk_code)
        return result

    def reform(self, temp_result):
        alpha = -1 * temp_result / temp_result.rolling(self.reform_window).min()
        return alpha
