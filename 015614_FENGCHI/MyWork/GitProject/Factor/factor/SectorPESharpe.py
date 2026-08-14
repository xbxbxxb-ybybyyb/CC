import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor

class SectorPESharpe(BaseFactor):
    depend_data = ["FactorData.Basic_factor.sw_indcode1", "FactorData.Basic_factor.pe_ttm"]
    reform_window = 10

    def calc_single(self, database):
        indcode = database.depend_data['FactorData.Basic_factor.sw_indcode1']
        pe = database.depend_data['FactorData.Basic_factor.pe_ttm']
        indcode, pe = indcode.iloc[-1], pe.iloc[-1]
        pe_ind = indcode.map(pe.groupby(indcode).mean())
        result = -(pe - pe_ind)
        return result

    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()
        return alpha
