from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
import xfactor.Util as Util
import time
import copy

class ForecastEPChange60d(BaseFactor):

    factor_type = "DAY"
    depend_data = ["FactorData.Basic_factor.close","FactorData.FCD_CHINA_STOCK_DAILY_SUNTIME"]

    lag = 0
    financial_lag = 60

    def calc_single(self,database): 
        close = database.depend_data['FactorData.Basic_factor.close']
        
        con_forecast_stk = database.depend_data['FactorData.FCD_CHINA_STOCK_DAILY_SUNTIME']
        
        ind = np.where(con_forecast_stk['C4_TYPE'].values<=2)[0]
        con_forecast_stk = con_forecast_stk.iloc[ind]
        con_forecast_stk = con_forecast_stk.reset_index()[['date','stock','RPT_DATE','C5','C4_TYPE']]
        report_year = con_forecast_stk[['stock','date','RPT_DATE']].iloc[np.where(con_forecast_stk['C4_TYPE'].values==0)[0]]
        report_year['RPT_DATE'] = report_year['RPT_DATE'].values+1
        report_year = report_year.groupby(['date','stock'],as_index=False)['RPT_DATE'].first()

        multiind = pd.MultiIndex.from_arrays(con_forecast_stk[['date','stock','RPT_DATE']].values.T, names=('date', 'stock','RPT_DATE'))
        con_forecast_stk.index= multiind
        multiind2 = pd.MultiIndex.from_arrays(report_year[['date','stock','RPT_DATE']].values.T, names=('date', 'stock','RPT_DATE'))

        con_forecast_stk = con_forecast_stk.loc[multiind2,['C5']].reset_index()
        multiind3 = pd.MultiIndex.from_arrays(con_forecast_stk[['date','stock']].values.T, names=('date', 'stock'))
        con_forecast_stk.index= multiind3
        C5 = con_forecast_stk['C5'].unstack()
        C5 = C5.reindex(close.columns,axis=1)

        return C5.mean()/C5.iloc[-1]