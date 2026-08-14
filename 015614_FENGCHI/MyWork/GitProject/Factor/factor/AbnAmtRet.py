# coding: utf-8

from xfactor.BaseFactor import BaseFactor
import statsmodels.api as sm
from copy import deepcopy
from datetime import datetime
import time
import pandas as pd
import numpy as np


class AbnAmtRet(BaseFactor):
    #  定义因子参数
    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.adjfactor",'FactorData.Basic_factor.amt_by_yuan']
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 120
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    """
    将amt大于abn_amt的当日涨跌幅设置为0，然后求60日内的平均值。abn_amt是平均值+0.66倍标准差
    """
    def calc_single(self, database):
        n =60
        adj_factor = database.depend_data['FactorData.Basic_factor.adjfactor']
        close = database.depend_data['FactorData.Basic_factor.close']*adj_factor
        amt  =database.depend_data['FactorData.Basic_factor.amt_by_yuan']
        ret = close / close.shift(1) - 1
        abn_amt = amt.rolling(window=n, min_periods=1).mean() + amt.rolling(window=n,
                                                                                 min_periods=1).std() * 0.66
        ret[amt < abn_amt] = 0
        factor_data = ret.rolling(window=n).sum()
        return factor_data.iloc[-1,:]

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean()

    def cal_residual(self, data_array):
        x = data_array[:-1]
        y = data_array[1:]
        beta = y.std() / x.std() * np.corrcoef(x,y)[0,1]
        alpha = y.mean() - beta * x.mean()
        residual = y[-1] - (alpha + beta * x[-1])
        return -residual