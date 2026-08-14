from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
 
class ODPB_DIFF20(BaseFactor):

 
    factor_type = "DAY"

    s_SunTime = 'FactorData.SUNTIME_stock_order3'
    s_close = 'FactorData.Basic_factor.close'
    
    depend_data = [s_SunTime,s_close]

    financial_lag = 150 
    
    #reform_window = 20
     
    def calc_single(self, database):
        data_old = database.depend_data[self.s_SunTime]
                                        
        ##选取报告发布日前的信息
        data= data_old[['FORWARD_PB']]
        close= database.depend_data[self.s_close]  
        
        data = data.unstack()
        
        columns_new=[x[1] for x in data.columns.to_list()]
        
        data.columns=columns_new
           
        ###按照日期排序
        data.sort_index(inplace=True)
      
        def find_diff(rb):
            ##选取第一行
            df_factor1=rb[0]               
            ##选取倒数第二行
            df_factor2=rb[-2]            
            result=(df_factor2-df_factor1)/abs(df_factor1)           
            return result
        
        datatemp2=data.rolling(20).apply(find_diff)
    
        ###直接选取最后一行
        factor=datatemp2.iloc[-1,]
        factor = factor.reindex(close.columns)
                          
        return -factor
     
    def reform(self, temp_result):
        return temp_result