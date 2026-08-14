from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
 
class FM10_GTGTTM(BaseFactor):

 
    factor_type = "DAY"
    # 定义万得A股财务指标数据库的名称
    s_Wind = 'FactorData.FDD_CHINA_STOCK_QUARTERLY_WIND.gctogr_ttm2'
    s_close = 'FactorData.Basic_factor.close'
    
    depend_data = [s_Wind,s_close]

    financial_lag = 800 # financial_lag需保证至少获取到一个季度的财度数据
    #reform_window = 20
     
    def calc_single(self, database):
        data_old = database.depend_data[self.s_Wind]
                                        
        ##选取报告发布日前的信息
        data= data_old[['gctogr_ttm2']]
        close= database.depend_data[self.s_close]  
        
        data = data.unstack()
        
        columns_new=[x[1] for x in data.columns.to_list()]
        
        data.columns=columns_new
           
        ###按照日期排序
        data.sort_index(inplace=True)
      
        #第一步运算：同比运算
        datatemp2=(data-data.shift(periods=4))/abs(data.shift(periods=4))
          
        ##第二步运算：（最新值-4期平均）/标准差
        datatemp2=(datatemp2-datatemp2.rolling(4).mean())/datatemp2.rolling(4).std()
       
        ###如果有na，前值填充
        datatemp2.fillna(method='pad',inplace=True)
    
        ###直接选取最后一行
        factor=datatemp2.iloc[-1,]
        factor = factor.reindex(close.columns)                            
                          
        return -factor
     
    def reform(self, temp_result):
        return temp_result