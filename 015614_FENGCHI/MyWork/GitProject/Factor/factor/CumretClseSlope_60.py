from xfactor.BaseFactor import BaseFactor
import statsmodels.api as sm
from copy import deepcopy
from datetime import datetime
import time
import pandas as pd
import numpy as np
from xfactor.FixUtil import min_forward_adj

class CumretClseSlope_60(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 59

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        def getslope(subret):
            tm_id = list(range(len(subret)))
            x = sm.add_constant(tm_id)
            subslope = sm.OLS(subret, x).fit().params.ix['x1',:]
            subslope = (subslope).astype(np.float64)
            subslope = subslope[~np.isinf(subslope)]
            subslope.index = subret.columns
            return subslope
        cls_minute = database.depend_data['FactorData.Basic_factor.close_minute'].copy()
        cls_minute = min_forward_adj(cls_minute)
        date_series = pd.Series([datetime.strftime(i,'%Y%m%d') for i in cls_minute.index],index = cls_minute.index)
        cls_minute.drop(date_series.groupby(date_series).head(1).index,inplace=True)
        cls_minute.drop(date_series.groupby(date_series).tail(1).index,inplace=True)
        divided = np.tile(cls_minute.values[0,:],(cls_minute.shape[0],1))
        subret = cls_minute.values/divided
        subret = pd.DataFrame(subret,index = cls_minute.index, columns = cls_minute.columns)
        date_series = pd.Series([datetime.strftime(i, '%Y%m%d') for i in subret.index], index=subret.index)
        sng_slope = subret.iloc[:, :-1].groupby(date_series).apply(getslope)
        ans = -sng_slope.mean()
        return ans
