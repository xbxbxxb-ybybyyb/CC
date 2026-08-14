from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
import math

class PROFIT_UP60(BaseFactor):

 
    factor_type = "DAY"

    s_SunTime = 'FactorData.SUNTIME_cmb_report_adjust'
    
    s_close = 'FactorData.Basic_factor.close'
    
    depend_data = [s_SunTime,s_close]

    financial_lag = 100
    
    #reform_window = 20
     
    def calc_single(self, database):
        datatemp = database.depend_data[self.s_SunTime]
                                        
        close= database.depend_data[self.s_close]  
        
        ##
        datelist=datatemp.index.get_level_values(0).unique().to_list()
        datelist.sort()
        datelist=datelist[-60:-1]
        
        ##选取报告发布日前的信息        
        datatemp['code']=datatemp.index.get_level_values(1)
        
        datatemp['tradingday']=datatemp.index.get_level_values(0)   
              
        datatemp=datatemp[datatemp.tradingday.isin(datelist)]           
                
        datatemp['score_dif']=(datatemp['CURRENT_FORECAST_EPS']-datatemp['PREVIOUS_FORECAST_EPS'])/abs(datatemp['PREVIOUS_FORECAST_EPS'])
       
        datatemp=datatemp[datatemp['score_dif'].notnull()]
        
        datatemp['score_dif']=datatemp['score_dif'].apply(lambda x: 0 if math.isinf(x) else x)       
                
        grouped = pd.DataFrame(datatemp[['score_dif']].groupby(datatemp['code']).mean())
                  
        factor=pd.Series(grouped['score_dif'].values,index=grouped.index)

                  
        ##reindex 
        factor = factor.reindex(close.columns)                            
        return factor
     
    def reform(self, temp_result):
        return temp_result