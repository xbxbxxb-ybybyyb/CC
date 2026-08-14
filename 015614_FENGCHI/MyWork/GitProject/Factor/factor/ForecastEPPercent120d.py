from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class ForecastEPPercent120d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.SUNTIME_con_forecast_c2_stk"]

    lag = 0
    financial_lag = 120

    def calc_single(self,database): 
        close = database.depend_data['FactorData.Basic_factor.close']
        con_forecast_c2_stk = database.depend_data['FactorData.SUNTIME_con_forecast_c2_stk']
        C9 = con_forecast_c2_stk['C9'].unstack().fillna(method='ffill')
        C9 = C9.reindex(close.columns, axis = 1)
        ep = pd.DataFrame(1/C9.values,index=C9.index,columns=C9.columns)
        ep_percent = ep.rank(pct=True).iloc[-1]

        return ep_percent

