from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util


class ForecastPEGDelta5d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.SUNTIME_con_forecast_c3_stk"]

    lag = 0
    financial_lag = 5

    def calc_single(self,database): 
        close = database.depend_data['FactorData.Basic_factor.close']
        con_forecast_c3_stk = database.depend_data['FactorData.SUNTIME_con_forecast_c3_stk']
        CGPEG = con_forecast_c3_stk['CGPEG'].unstack().fillna(method='ffill')
        CGPEG = CGPEG.reindex(close.columns, axis = 1)
        
        epg = pd.DataFrame(1./CGPEG.values,index=CGPEG.index,columns=CGPEG.columns)
        peg_delta = epg.iloc[-1]-epg.iloc[-5]

        return peg_delta

