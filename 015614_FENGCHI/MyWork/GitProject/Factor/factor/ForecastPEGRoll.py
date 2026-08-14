from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class ForecastPEGRoll(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.SUNTIME_con_forecast_c3_stk"]

    lag = 0
    financial_lag = 0

    def calc_single(self,database): 
        close = database.depend_data['FactorData.Basic_factor.close']
        con_forecast_c3_stk = database.depend_data['FactorData.SUNTIME_con_forecast_c3_stk']
        CGPEG = con_forecast_c3_stk['CGPEG'].unstack().fillna(method='ffill').iloc[0]
        CGPEG = CGPEG.reindex(close.columns)

        return -CGPEG
