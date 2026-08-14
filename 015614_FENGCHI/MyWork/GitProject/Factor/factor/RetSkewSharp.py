from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as ut
import pandas as pd


class RetSkewSharp(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 10

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        fmt = '%Y-%m-%d'
        date_list = np.unique(minute_close.index.strftime(fmt))
        result_df = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=minute_close.columns)

        for date in date_list:
            close_df = minute_close.loc[date]
            close_df = close_df.resample('5T').last()
            return_df = close_df.pct_change(periods=1)

            skew = return_df.iloc[-30:].skew()
            if len(skew.dropna()) != 0:
                result_df.loc[date] = skew
            else:
                result_df.loc[date] = 0.0

        ans = result_df.iloc[-1, :]
        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        temp = temp_result.rolling(10, min_periods=1).mean()/temp_result.rolling(10, min_periods=1).std()
        temp1 = -abs(temp)
        return temp1

