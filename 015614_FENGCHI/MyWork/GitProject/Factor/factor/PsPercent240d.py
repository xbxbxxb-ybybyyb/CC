from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from collections import Counter


class PsPercent240d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.ps_ttm"]

    lag = 240

    def calc_single(self,database): 
        ps_ttm = database.depend_data['FactorData.Basic_factor.ps_ttm']
        PsPercent = ps_ttm.rank(axis=0,pct=True).iloc[-1]

        return -PsPercent



