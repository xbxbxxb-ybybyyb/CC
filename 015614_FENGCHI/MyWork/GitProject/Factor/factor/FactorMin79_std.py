from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as Util
import xfactor.FixUtil as FixUtil

import pandas as pd

class FactorMin79_std(BaseFactor):
    #  定义因子参数
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    ##fix_times = ["1000","1100","1300","1330","1400","1430"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.limit_status_minute',"FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.open_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    ##
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        
      
        FixUtil.minute_data_transform( database.depend_data, operation=['merge', 'merge'])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mclose = Util.data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        data1 = FixUtil.min_forward_adj(mclose)
        data2 = Util.data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'],limit_status,method='minute')
        mopen = Util.data_filter(database.depend_data['FactorData.Basic_factor.open_minute'],limit_status,method='minute')
        data3 = FixUtil.min_forward_adj(mopen)             
        ##获取时间
        fmt = '%Y-%m-%d'
        date_list = np.unique(data1.index.strftime(fmt))
        last_date = date_list[-2]
        current_date = date_list[-1]
        data1 = data1.loc[last_date].append(data1.loc[current_date])
        data2 = data2.loc[last_date].append(data2.loc[current_date]) 
               
      
        data3_temp=(data3.values-data3.shift(periods=1).values)/abs(data3.shift(periods=1).values)   
      

        data11=data1[pd.DataFrame((data3_temp<0),columns=data1.columns,index=data1.index)]
        data21=data2[pd.DataFrame((data3_temp<0),columns=data1.columns,index=data1.index)]        
             
        ans =Util.array_coef(data11,data21)      
    
              
        return ans
        
# 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).std()
        
        
        