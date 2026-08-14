from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
import math
from xquant.factordata import FactorData

class PROFIT_PER20(BaseFactor):

 
    factor_type = "DAY"

    s_SunTime = 'FactorData.SUNTIME_cmb_report_adjust'
    
    s_close = 'FactorData.Basic_factor.close'
    
    depend_data = [s_SunTime,s_close]

    financial_lag = 40

    #reform_window = 20
     
    def calc_single(self, database):
        
        datatemp = database.depend_data[self.s_SunTime]
        
        close= database.depend_data[self.s_close]  
        
        ##
        datelist=datatemp.index.get_level_values(0).unique().to_list()
        datelist.sort()
        datelist=datelist[-20:-1]
        
        ##选取报告发布日前的信息        
        datatemp['code']=datatemp.index.get_level_values(1)
        
        datatemp['tradingday']=datatemp.index.get_level_values(0)   
              
        datatemp=datatemp[datatemp.tradingday.isin(datelist)]      
        
        datatemp['score_dif']=(datatemp['CURRENT_FORECAST_EPS']-datatemp['PREVIOUS_FORECAST_EPS'])/abs(datatemp['PREVIOUS_FORECAST_EPS'])
       
        datatemp=datatemp[datatemp['score_dif'].notnull()]
        
        datatemp['score_dif']=datatemp['score_dif'].apply(lambda x: 0 if math.isinf(x) else x)       
        
        ##新加2个参数，方便后面因子计算
        datatemp['num1']=1
   
        datatemp['num2']=0
     
        datatemp.loc[(datatemp.score_dif>0),'num2']=1
          
        datatemp.loc[(datatemp.score_dif<0),'num2']=-1
        
        
        grouped = pd.DataFrame(datatemp[['num1','num2']].groupby(datatemp['code']).sum())
                  
        factor=pd.Series(grouped['num2'].values/grouped['num1'].values,index=grouped.index)
        
        ##reindex 
        factor = factor.reindex(close.columns)
        
        return factor
     
    def reform(self, temp_result):
        return temp_result