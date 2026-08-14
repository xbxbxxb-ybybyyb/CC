# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class AmtDealReDiff5d(BaseFactor):
    
    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close", "FactorData.Basic_factor.amt", "FactorData.Basic_factor.dealnum", 
    "FactorData.Basic_factor.adjfactor"]
    lag = 41
    reform_window = 5

    def calc_single(self, database):
        adjfactor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close']*adjfactor
        amt = database.depend_data['FactorData.Basic_factor.amt']
        dealnum = database.depend_data['FactorData.Basic_factor.dealnum']
        

        n = 40
        rho = 0.8
        amt_deal = amt / dealnum
        
        re = close/close.shift(1)
        date = close.index
        re = re.iloc[-n:]
        amt_deal = amt_deal.iloc[-n:]
        
        a_index = np.where(amt_deal.values > amt_deal.quantile(rho).values, re.values, np.nan)
        alpha_a = pd.DataFrame(a_index,index=amt_deal.index,columns=amt_deal.columns).product(skipna=True)
        b_index = np.where(amt_deal.values < amt_deal.quantile(1-rho).values, re.values, np.nan)
        alpha_b = pd.DataFrame(b_index,index=amt_deal.index,columns=amt_deal.columns).product(skipna=True)
        
        alpha = alpha_a-alpha_b
        alpha = np.where(amt_deal.values[-1]>0,alpha.values,np.nan)
        return -pd.Series(alpha,index=close.columns)

    def reform(self, temp_result):
        A = temp_result.rolling(self.reform_window, min_periods=1).mean()
        return A