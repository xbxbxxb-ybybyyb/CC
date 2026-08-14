from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
from xfactor.Util import data_filter


class BuyAmtStd3Day(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.buytradeamt_minute',
                   'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.limit_status_minute',]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。


    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        period = '5min'
        minute_data_transform(database.depend_data,['drop1','drop4'])
        limit_status = database.depend_data["FactorData.Basic_factor.limit_status_minute"].copy()
        b_amt = database.depend_data["FactorData.Basic_factor.buytradeamt_minute"].copy().iloc[-237*self.lag:,:]
        amt = database.depend_data["FactorData.Basic_factor.amt_minute"].copy().iloc[-237*self.lag:,:]
        b_amt = data_filter(b_amt,limit_status,method='minute')
        amt = data_filter(amt,limit_status,method='minute')
        filter_index = b_amt.resample(period,how='last').dropna(axis=0,how='all').index
        b_amt_min = b_amt.resample(period).sum().reindex(filter_index)
        amt_min = amt.resample(period).sum().reindex(filter_index)
        b_ratio = b_amt_min/amt_min
        ans = b_ratio.std()
        amt_min[amt_min.values == 0] = np.nan
        ans2 = self.get_res(ans,np.log(amt_min).std())
        return ans2

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。


    def get_res(self,y: pd.Series, x: pd.Series, intersect=True):
        y_isnan = np.isnan(y)
        x_isnan = np.isnan(x)
        y_isvalid = 1 - y_isnan
        x_isvalid = 1 - x_isnan
        valids = x_isvalid * y_isvalid
        y_valid = y[valids == 1]
        x_valid = x[valids == 1]
        if intersect:
            x_valid = np.array([np.ones(x_valid.shape), x_valid]).T
            if np.linalg.det(x_valid.T.dot(x_valid)) == 0:
                residual = pd.Series(np.zeros(y.shape) * np.nan, index=y.index)
            else:
                b = np.linalg.inv(x_valid.T.dot(x_valid)).dot(x_valid.T).dot(y_valid)
                residual = y_valid - x_valid.dot(b)
                residual = residual.reindex(y.index)
        else:
            x_valid = x_valid.T
            if np.linalg.det(x_valid.T.dot(x_valid)) == 0:
                residual = pd.Series(np.zeros(y.shape) * np.nan, index=y.index)
            else:
                b = x_valid.T.dot(y_valid) / (x_valid.T.dot(x_valid))
                residual = y_valid - x_valid * b
                residual = residual.reindex(y.index)
        return residual