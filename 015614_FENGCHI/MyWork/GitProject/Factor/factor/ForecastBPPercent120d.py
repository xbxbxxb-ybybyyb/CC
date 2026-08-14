from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class ForecastBPPercent120d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.SUNTIME_con_forecast_c3_stk"]

    lag = 0
    financial_lag = 120

    def calc_single(self,database): 
        close = database.depend_data['FactorData.Basic_factor.close']
        con_forecast_c3_stk = database.depend_data['FactorData.SUNTIME_con_forecast_c3_stk']
        CGPB = con_forecast_c3_stk['CGPB'].unstack().fillna(method='ffill')
        CGPB = CGPB.reindex(close.columns, axis = 1)
        
        bp = pd.DataFrame(1/CGPB.values,index=CGPB.index,columns=CGPB.columns)
        bp_percent = bp.rank(pct=True).iloc[-1]

        return bp_percent

