from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
import time

class ForecastPE(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.FCD_CHINA_STOCK_DAILY_SUNTIME"]

    lag = 0
    financial_lag = 0

    def calc_single(self,database): 
        # t0 = time.time()
        close = database.depend_data['FactorData.Basic_factor.close']
        date = close.index[-1]
        
        con_forecast_stk = database.depend_data['FactorData.FCD_CHINA_STOCK_DAILY_SUNTIME'].loc[(date,)]
        ind = np.where(con_forecast_stk['C4_TYPE'].values<=2)[0]
        con_forecast_stk = con_forecast_stk.iloc[ind]
        report_year = con_forecast_stk['RPT_DATE'].iloc[np.where(con_forecast_stk['C4_TYPE'].values==0)[0]]+1
        report_year = pd.DataFrame(report_year.values,index=report_year.index,columns=['report_year'])
        report_year['stock'] = report_year.index.tolist()
        report_year = report_year['report_year'].groupby(['stock']).first()
        
        report_year = report_year.reindex(con_forecast_stk.index.tolist())

        ind = np.where(con_forecast_stk['RPT_DATE'].values==report_year.values)[0]
        con_forecast_stk = con_forecast_stk.iloc[ind]
    
        C5 = con_forecast_stk['C5']
        C5 = C5.reindex(close.columns)

        # print(time.time()-t0)
        return -C5