from xfactor.BaseFactor import BaseFactor
import numpy as np
import xfactor.Util as ut
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
from xfactor.Util import *

class RetVolCVMultiple(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.limit_status_minute"]
    # 依赖的个人因子库的因子，默认为空，可不设置
    # depend_factors = ["SampleFactor"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 5

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation=["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        minute_volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'], limit_status,
                                    method='minute')
        minute_close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'], limit_status,
                                   method='minute')

        ret_cs = minute_close.iloc[-1] / minute_close.iloc[-27] - 1
        vol_cv = (minute_volume.iloc[-27:, ]).std() / (minute_volume.iloc[-27:, ]).mean()
        multiple = ret_cs * vol_cv

        return multiple

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()

