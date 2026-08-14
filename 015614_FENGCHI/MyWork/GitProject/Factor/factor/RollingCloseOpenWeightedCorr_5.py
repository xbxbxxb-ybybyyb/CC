from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class RollingCloseOpenWeightedCorr_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.open_minute","FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=0
    reform_window=7

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']


        # 播放的数据通过database.depend_data字典获取
        minute_close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        minute_close = min_forward_adj(minute_close)
        close = minute_close.resample("5T", label="right").last().dropna(axis=0, how='all').values
        minute_open = data_filter(database.depend_data['FactorData.Basic_factor.open_minute'],limit_status,method='minute')
        minute_open = min_forward_adj(minute_open)
        open = minute_open.resample("5T", label="right").first().dropna(axis=0, how='all').values

        minute_ret = close[1:,:] / open[:-1,:] -1
        ans_df = minute_ret.std(axis=0)

        current_date = minute_close.index[-1].strftime('%Y-%m-%d')
        df_factor = pd.DataFrame(index=[pd.Timestamp(current_date)], columns=minute_close.columns)
        df_factor.loc[current_date,:] = ans_df
        return df_factor.iloc[0,:]


    def reform(self, temp_result):
        
        ret_std = temp_result  # 传入这里的函数每天都会调用一次播放数据计算中间量
        stock_minute_cov1 = ret_std.rolling(window=self.reform_window-2, min_periods=1).cov(ret_std.shift(1))
        stock_minute_cov2 = ret_std.rolling(window=self.reform_window-2, min_periods=1).cov(ret_std.shift(2))
        factor_values = ret_std.rolling(window=self.reform_window-2, min_periods=1).std() + 2 * (
                2 / 3 * stock_minute_cov1 + 1 / 3 * stock_minute_cov2)
        return factor_values


