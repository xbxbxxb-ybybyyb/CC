from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np

class MinuteRetVolMultSkewSharpe(BaseFactor):

    """
    * 因子名：MinuteRetVolMultSkewSharpe
    * 因子功能描述：计算最后两小时收益与成交量占比之积之偏度之10日夏普。
    * 因子参数：MinuteClose
    * 作者：姚逸凡
    * 因子创建日期： 2019.1.15
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "DAY"
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_volume_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_close_min, s_volume_min]
    n = 10
    reform_window = 20
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        volume_min = database.depend_data[self.s_volume_min]
        result = self.minute(close_min, volume_min)
        # result = result.rolling(20,1).skew()
        # result = self.Mean(result, 10) / self.Stdev(result, 10)

        return result
    
    def reform(self, temp_result):
        res = temp_result.rolling(self.reform_window, 1).skew()
        return self.Mean(res, self.n) / self.Stdev(res, self.n)

    def Mean(self, DF, lag):

        meanDF = DF.rolling(window=lag, min_periods=1).mean()
        return meanDF

    def Stdev(self,DF, lag):

        stdDF = DF.rolling(window=lag, min_periods=1).std()
        return stdDF

    def minute(self, MinuteClose,MinuteVolume):

        # fmt = '%Y-%m-%d'
        # date_list = np.unique(MinuteClose.index.strftime(fmt))
        # volDF = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
        # returnDF = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)

        n = 120
        # for date in date_list:
        closedf = MinuteClose
        volumedf = MinuteVolume

        returndf = (closedf.iloc[-1] - closedf.iloc[-n]) / closedf.iloc[-n]
        vol_last = volumedf[-n:].sum(axis=0) / volumedf.sum(axis=0)
        if len(vol_last.dropna()) != 0:
            volDF = vol_last
        else:
            volDF = 0.0
        # returnDF.loc[date] = returndf
        # resultDF = -volDF * returnDF
        return -volDF * returndf


