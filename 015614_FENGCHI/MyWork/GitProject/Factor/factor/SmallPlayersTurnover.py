from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class SmallPlayersTurnover(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 'FactorData.WIND_AShareMoneyFlow',
                    'FactorData.Basic_factor.free_float_shares',
                    'FactorData.Basic_factor.is_valid']
                    

    financial_lag = 1
    lag = 0
    reform_window = 0

    def calc_single(self, database):

        moneyflow = database.depend_data['FactorData.WIND_AShareMoneyFlow']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]

        moneyflow['small'] = moneyflow['BUY_VOLUME_SMALL_ORDER']+moneyflow['SELL_VOLUME_SMALL_ORDER']
        free_float_shares.index = pd.to_datetime(free_float_shares.index)
        moneyflow_small = moneyflow['small'].unstack().reindex(index = free_float_shares.index, columns=free_float_shares.columns)
        
        moneyflow_small_turn = moneyflow_small/free_float_shares

        return -moneyflow_small_turn.iloc[-1][valid]
 