from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class BigPlayersVwap(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 'FactorData.WIND_AShareMoneyFlow',
                    'FactorData.Basic_factor.amt',
                    'FactorData.Basic_factor.volume',
                    'FactorData.Basic_factor.adjfactor',
                    'FactorData.Basic_factor.is_valid']
                    

    financial_lag = 5
    lag = 0
    reform_window = 0

    def calc_single(self, database):

        moneyflow = database.depend_data['FactorData.WIND_AShareMoneyFlow']
        amt = database.depend_data['FactorData.Basic_factor.amt']
        volume = database.depend_data['FactorData.Basic_factor.volume']
        vwap = amt/volume/10
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]

        moneyflow['bigvwap'] = (moneyflow['BUY_VALUE_EXLARGE_ORDER']+moneyflow['SELL_VALUE_EXLARGE_ORDER'])/(moneyflow['BUY_VOLUME_EXLARGE_ORDER']+moneyflow['SELL_VOLUME_EXLARGE_ORDER'])
        
        
        vwap.index = pd.to_datetime(vwap.index)
        moneyflow_big = moneyflow['bigvwap'].unstack().reindex(index = vwap.index, columns=vwap.columns)
        
        moneyflow_big_vwapratio = moneyflow_big/vwap-1

        return -moneyflow_big_vwapratio.iloc[-1][valid]
 