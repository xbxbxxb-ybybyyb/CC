from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import xfactor.FixUtil as FixUtil

class MinEMVA(BaseFactor):    # 派生一个因子类
    factor_type = 'DAY'         
    # 声明因子类型为DAY
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.close"]
 
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    reform_window = 20
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    def calc_single(self, database):
        
        mhigh = database.depend_data['FactorData.Basic_factor.high_minute'].copy()
        mlow = database.depend_data['FactorData.Basic_factor.low_minute'].copy()
        volume_df = database.depend_data['FactorData.Basic_factor.volume_minute'].copy()
        day_close=database.depend_data['FactorData.Basic_factor.close'].copy()
        
        high_df = FixUtil.min_forward_adj(mhigh)
        low_df = FixUtil.min_forward_adj(mlow)
        

        high_df = high_df.values / high_df.mean().values
        low_df = low_df.values / low_df.mean().values
        volume_df = volume_df.values / volume_df.mean().values
        swing_range = high_df - low_df
        mid_price = pd.DataFrame((high_df + low_df) / 2,columns=mhigh.columns,index=mhigh.index)
        
        ans = pd.DataFrame((volume_df * swing_range * (mid_price.values - mid_price.shift(1).values)),columns=mid_price.columns,index=mid_price.index).mean()
            
        return -ans
     
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,min_periods=10).mean()
        