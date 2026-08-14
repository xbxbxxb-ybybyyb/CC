from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteVolofVolumeHHI(BaseFactor):

    """
    * 因子名：MinuteVolofVolumeHHI
    * 因子功能描述：计算日内成交量HHI指数的10日标准差。 hhi = Sum(Xi^2/(Sum(Xi)^2))，用来衡量X的离散程度，hhi越大则越离散。
    * 因子参数：MinuteVolume
    * 作者：姚逸凡
    * 因子创建日期： 2019.1.15
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = 'DAY'
    s_vol_min = 'FactorData.Basic_factor.volume_minute'
    s_close = 'FactorData.Basic_factor.close'
    depend_data = [s_vol_min, s_close]
    reform_window = 10
    lag = 5
    # minute_lag =1
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        vol_min = database.depend_data[self.s_vol_min]
        close = database.depend_data[self.s_close]
        print(vol_min.shape)
        print(close.shape)
        result = self.minute(vol_min)

        return result
    
    def reform(self, temp_result):
        return -self.Stdev(temp_result, self.reform_window)

    def Mean(self, DF, lag):

        meanDF = DF.rolling(window=lag, min_periods=1).mean()
        return meanDF

    def Stdev(self,DF, lag):

        stdDF = DF.rolling(window=lag).std()
        return stdDF

    def minute(self, MinuteVolume):

            volume_df = MinuteVolume
            volume_df = volume_df.resample('10T').sum()
            volume_df = volume_df.tail(15)
            volume_sum_squared = np.square(volume_df.sum(axis=0))
            volume_squared = np.square(volume_df)
            hhi = (volume_squared / volume_sum_squared).sum(axis=0)
            return hhi

            # if len(hhi.dropna()) != 0:
            #     result_df.loc[date] = hhi
            # else:
            #     result_df.loc[date] = 0.0



