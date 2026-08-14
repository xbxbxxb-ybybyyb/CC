from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class TargetReturnDelta5d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.SUNTIME_con_forecast_schedule"]

    lag = 5
    financial_lag = 5

    def calc_single(self,database): 
        close = database.depend_data['FactorData.Basic_factor.close']
        con_forecast_schedule = database.depend_data['FactorData.SUNTIME_con_forecast_schedule']
        con_forecast_schedule = con_forecast_schedule[con_forecast_schedule['TARGET_PRICE_TYPE']<=3]
        TARGET_PRICE = con_forecast_schedule['TARGET_PRICE'].unstack()
        TARGET_PRICE = TARGET_PRICE.reindex(close.columns,axis=1)
        
        target_return = TARGET_PRICE/close
        
        return target_return.iloc[-1]-target_return.iloc[0]