
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import pandas as pd
import numpy as np


class QfaROE(BaseFactor):
    #  定义因子参数

    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    s_Wind = 'FactorData.FDD_CHINA_STOCK_QUARTERLY_WIND.qfa_roe'
    depend_data = [s_Wind]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    financial_lag = 200
    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        data_old = database.depend_data[self.s_Wind]

        ##选取报告发布日前的信息
        data = data_old[['qfa_roe']]
        data = data.unstack()
        columns_new = [x[1] for x in data.columns.to_list()]
        data.columns = columns_new

        ###按照日期排序
        data.sort_index(inplace=True)
        factor = data.iloc[-1,]
        factor = factor.reindex(data.columns)
        return factor
