from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as Util
import xfactor.FixUtil as FixUtil

import pandas as pd

class FactorMin133_std(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    ##fix_times = ["1000","1030","1400","1430"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.limit_status_minute',"FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    ##
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        
      
        FixUtil.minute_data_transform( database.depend_data, operation=['merge', 'merge'])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        mclose = database.depend_data['FactorData.Basic_factor.close_minute'].copy()
        mclose = Util.data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        data1 = FixUtil.min_forward_adj(mclose)
        mopen = database.depend_data['FactorData.Basic_factor.open_minute'].copy()
        data2 = FixUtil.min_forward_adj(mopen)
        mhigh = database.depend_data['FactorData.Basic_factor.high_minute'].copy()
        mhigh = Util.data_filter(database.depend_data['FactorData.Basic_factor.high_minute'],limit_status,method='minute')
        data3 = FixUtil.min_forward_adj(mhigh)        
        mlow = database.depend_data['FactorData.Basic_factor.low_minute'].copy()
        mlow = Util.data_filter(database.depend_data['FactorData.Basic_factor.low_minute'],limit_status,method='minute')
        data4 = FixUtil.min_forward_adj(mlow)
        ##获取时间
        fmt = '%Y-%m-%d'
        date_list = np.unique(data1.index.strftime(fmt))
        last_date = date_list[-2]
        current_date = date_list[-1]
        data1 = data1.loc[last_date].append(data1.loc[current_date])
        data2 = data2.loc[last_date].append(data2.loc[current_date])
        data3 = data3.loc[last_date].append(data3.loc[current_date])
        data4 = data4.loc[last_date].append(data4.loc[current_date])

        ##最近30分钟蜡烛线比例
        data1_current=data1.iloc[-30:]
        data2_current=data2.iloc[-30:]

        ##白色蜡烛线
        white_current=data1_current>data2_current   
        
        ##30分钟前
        data2_last=data2.iloc[:-30]
        data3_last=data3.iloc[:-30]   
        data1_last=data1.iloc[:-30]   
        data4_last=data4.iloc[:-30]   

        ##star
        ##十字星占比
        star=(data3_last-data4_last)/abs(data1_last-data2_last)
        
        condition=star>5    
        
        Per=white_current.apply(sum)/white_current.shape[0]+condition.apply(sum)/condition.shape[0]
        
       
        ans =Per
 
        return ans
        
# 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).std()
        
        
        