from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np
 
class FM15_EPS(BaseFactor):

 
    factor_type = "DAY"
    # 定义万得A股财务指标数据库的名称
    s_Wind = 'FactorData.FDD_CHINA_STOCK_QUARTERLY_WIND.eps_basic'
    s_close = 'FactorData.Basic_factor.close'
    
    depend_data = [s_Wind,s_close]
    financial_lag = 800 # financial_lag需保证至少获取到一个季度的财度数据
    #reform_window = 20
     
    def calc_single(self, database):
        data_old = database.depend_data[self.s_Wind]
                                        
        ##选取报告发布日前的信息
        data= data_old[['eps_basic']]
        close= database.depend_data[self.s_close]  
        
        data = data.unstack()
        
        columns_new=[x[1] for x in data.columns.to_list()]
        
        data.columns=columns_new
        
        ##写个简单的函数将数据处理成季度数据
        for j in range(1,data.shape[0]):       
              if str(data.index[j])[6]=='3':
                 pass
              else:
                 data.iloc[j,]=data.iloc[j,]-data.iloc[j-1,]
                 
        ##按照日期再排序一次          
        data.sort_index(inplace=True)   
        
        ##(最新值-均值)/std
        datatemp2=(data-data.rolling(4).mean())/data.rolling(4).std()         

        ###如果有na，前值填充
        datatemp2.fillna(method='pad',inplace=True)
    
        ###直接选取最后一行
        factor=datatemp2.iloc[-1,]
        factor = factor.reindex(close.columns)                            
                          
        return factor
     
    def reform(self, temp_result):
        return temp_result