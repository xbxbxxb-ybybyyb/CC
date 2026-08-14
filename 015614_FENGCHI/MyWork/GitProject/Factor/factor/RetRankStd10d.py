# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import time

class RetRankStd10d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.vwap","FactorData.Basic_factor.adjfactor"]


    lag = 1
    reform_window = 10

    def calc_single(self,database):
        #minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        vwap = database.depend_data['FactorData.Basic_factor.vwap']*adjfactor
        
        re = pd.DataFrame((vwap/vwap.shift(1)).values-1,index=vwap.index,columns=vwap.columns)
        re_rank = re.rank(axis=1,pct=True).iloc[-1]
        
        return re_rank
    
    
    def reform(self, temp_result):
        A = -temp_result.rolling(self.reform_window, min_periods=1).std()
        return A