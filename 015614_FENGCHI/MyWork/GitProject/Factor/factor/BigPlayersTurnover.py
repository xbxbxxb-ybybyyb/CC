from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import copy
import time
from sklearn.preprocessing import scale



class BigPlayersTurnover(BaseFactor):
    
    factor_type = "DAY"
    depend_data = [ 'FactorData.WIND_AShareMoneyFlow',
                    'FactorData.Basic_factor.free_float_shares',
                    'FactorData.Basic_factor.is_valid']
                    

    financial_lag = 1
    lag = 0

    def calc_single(self, database):

        moneyflow = database.depend_data['FactorData.WIND_AShareMoneyFlow']
        free_float_shares = database.depend_data['FactorData.Basic_factor.free_float_shares']
        is_valid = database.depend_data['FactorData.Basic_factor.is_valid']
        valid = pd.DataFrame(is_valid.values==1, index=is_valid.index, columns=is_valid.columns).iloc[-1]

        moneyflow['large'] = moneyflow['BUY_VOLUME_EXLARGE_ORDER']+moneyflow['SELL_VOLUME_EXLARGE_ORDER']
        free_float_shares.index = pd.to_datetime(free_float_shares.index)
        moneyflow_large = moneyflow['large'].unstack().reindex(index = free_float_shares.index, columns=free_float_shares.columns)
        
        moneyflow_large_turn = moneyflow_large/free_float_shares

        return -moneyflow_large_turn.iloc[-1][valid]
  