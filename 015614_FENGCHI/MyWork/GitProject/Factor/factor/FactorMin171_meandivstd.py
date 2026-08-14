from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as Util
import xfactor.FixUtil as FixUtil
import pandas as pd

class FactorMin171_meandivstd(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    ##fix_times = ["1000","1030","1100","1300","1330","1400","1430"]
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.limit_status_minute', "FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
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
        mclose = Util.data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')\
        
        data1 = FixUtil.min_forward_adj(mclose)
        data2 = Util.data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'],limit_status,method='minute')

        ##获取时间
        fmt = '%Y-%m-%d'
        date_list = np.unique(data1.index.strftime(fmt))
        last_date = date_list[-2]
        current_date = date_list[-1]
        data1 = data1.loc[last_date].append(data1.loc[current_date])
        data2 = data2.loc[last_date].append(data2.loc[current_date])

        
        def quantile_flag_up_down(x,flag_dir):
            
            x=x.sort_values(ascending=flag_dir)
            
            x.iloc[0:round(x.shape[0]*0.3)]=1
            
            x.iloc[round(x.shape[0]*0.7):x.shape[0]]=-1
            
            return x
            
        ##收益率
        data1_r=(data1-data1.shift())/data1.shift()
        
        ##成交量打标记
        data2_flag=data2.apply(quantile_flag_up_down,flag_dir=False)
        
        ##量高的
        data1_r_up=data1_r[data2_flag>0]
        
        ##最低的
        data1_r_down=data1_r[data2_flag<0]

        ##最高的波动率-最低的波动率
        ans =data1_r_up.skew()-data1_r_down.skew()
                                        
        return ans
        
# 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return Util.rolling_process(temp_result,ptype = 'meandivstd',window=self.reform_window)
        
        