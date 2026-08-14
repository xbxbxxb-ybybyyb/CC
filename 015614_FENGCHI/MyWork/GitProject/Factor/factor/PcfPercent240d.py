from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
from collections import Counter


class PcfPercent240d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.pcf_ocf_ttm"]

    lag = 240

    def calc_single(self,database): 
        pcf_ocf_ttm = database.depend_data['FactorData.Basic_factor.pcf_ocf_ttm']
        PcfPercent = pcf_ocf_ttm.rank(axis=0,pct=True).iloc[-1]

        return -PcfPercent



