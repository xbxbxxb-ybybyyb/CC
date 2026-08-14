# -*- coding: utf-8 -*-

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
import time

class VolumeStdBias(BaseFactor):
    """
    * 因子名：VolumeStdBias
    * 因子功能描述：成交量的波动率相对近20天均值的偏差
    * 因子参数：amt, is_valid_raw
    * 作者：肖倩
    * 因子创建日期： 2019.1.25
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20

    def calc_single(self, database):
        volume = database.depend_data['FactorData.Basic_factor.volume']

        # volume_valid = volume[is_valid_raw==1]
        # factor = volume_valid.rolling(window=n, min_periods=1).std()
        # factor[factor==0]=np.nan
        # factor = 1/factor[is_valid_raw==1]
        # factor = factor-factor.rolling(window=n,min_periods=1).mean()
        # factor[np.isinf(factor)] = np.nan
        # factor = factor[is_valid_raw==1]
        return -volume.iloc[-1,:]

    def  reform(self, temp_result):
        factor = temp_result.rolling(window=5, min_periods=1).std()
        factor[factor==0]=np.nan
        factor = 1/factor
        factor = factor-factor.rolling(window=5,min_periods=1).mean()
        factor[np.isinf(factor)] = np.nan
        return factor

