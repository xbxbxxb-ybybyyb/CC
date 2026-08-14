import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""
    * 因子名：MinuteCloseMomentumSharpe
    * 因子功能描述：计算日内最后15分钟趋势强度的十日夏普
    * 因子参数：MinuteClose
    * 作者：姚逸凡
    * 因子创建日期： 2019.1.15
"""
class MinuteCloseMomentumSharpe(BaseFactor):
    factor_type = 'DAY'
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的基础数据
    lag = 0
    minute_lag = 0
    # 定义播放后对所有结果做后处理的rolling窗口长度，默认reform_window=1，可不设置
    reform_window = 10
    # fix_times = ["1500"]

    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    def calc_single(self, database):

        minute_data_transform(database.depend_data,operation=['drop','merge'])
        close_minute = database.depend_data['FactorData.Basic_factor.close_minute']

        rtn_last_15_values = (close_minute.iloc[-1].values - close_minute.iloc[-15].values) / close_minute.iloc[-15].values
        denominator_values = np.nansum((abs(close_minute.values - close_minute.shift(1).values)[-15:]),axis=0)

        ratio_values = rtn_last_15_values / denominator_values

        if sum(np.isnan(ratio_values)) == len(ratio_values):
            ratio_values = [1.0 for _ in range(len(ratio_values))]

        ans = pd.Series(ratio_values, index=close_minute.columns)

        return ans

    def reform(self, temp_result):
        sharpe_values = -temp_result.rolling(window=self.reform_window, min_periods=1).mean().values / temp_result.rolling(window=self.reform_window, min_periods=1).std().values
        
        return pd.DataFrame(data=sharpe_values,index=temp_result.index,columns=temp_result.columns)

    # def definition(self, MinuteClose):
    #
    #     result = self.minute_help(self.minute, 'MinuteCloseMomentumSharpe', MinuteClose)
    #     result = -result
    #     result = self.Mean(result, 10) / self.Stdev(result, 10)
    #
    #     return result
    #
    # def Mean(self, DF, lag):
    #
    #     meanDF = DF.rolling(window=lag, min_periods=1).mean()
    #     return meanDF
    #
    # def Stdev(self,DF, lag):
    #
    #     stdDF = DF.rolling(window=lag, min_periods=1).std()
    #     return stdDF
    #
    # def minute(self, MinuteClose):
    #
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     resultDF = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
    #
    #     n = 15
    #     for date in date_list:
    #         closedf = MinuteClose.loc[date]
    #         ret_last = (closedf.iloc[-1] - closedf.iloc[-n]) / closedf.iloc[-n]
    #         denominator = (abs(closedf - closedf.shift(1))[-n:]).sum()
    #         ratio = ret_last / denominator
    #         if len(ratio.dropna()) != 0:
    #             resultDF.loc[date] = ratio
    #         else:
    #             resultDF.loc[date] = 1.0
    #
    #     return resultDF


