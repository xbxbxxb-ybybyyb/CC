from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
from xfactor.Util import data_filter
import datetime as dt

class MomBigOrder3Day(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.close_minute',
                   'FactorData.Basic_factor.numtrade_minute',
                   'FactorData.Basic_factor.amt_minute',
                   'FactorData.Basic_factor.limit_status_minute',]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 2
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。


    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        threshold = 0.2    
        limit_status = database.depend_data["FactorData.Basic_factor.limit_status_minute"].copy()
        
        dealnum = database.depend_data['FactorData.Basic_factor.numtrade_minute'].copy()
        amt = database.depend_data['FactorData.Basic_factor.amt_minute'].copy()
        close = database.depend_data['FactorData.Basic_factor.close_minute'].copy()

        dealnum = data_filter(dealnum, limit_status, method='minute')
        amt = data_filter(amt, limit_status, method='minute')
        close = data_filter(close, limit_status, method='minute')
        
        close = min_forward_adj(close)
        ret = np.log(close/close.shift(1))
        
        for i in range(int(ret.shape[0]/242)):
            ret.iloc[242*i, :] = np.nan
        exc_morning = close.index.time != dt.time(9, 25)
        exc_afternoon = [item not in [dt.time(14, 57), dt.time(14, 58), dt.time(14, 59), dt.time(15, 00)] for item in close.index.time]
        
        dealnum = dealnum.loc[np.logical_and(exc_morning, exc_afternoon)].copy()
        amt = amt.loc[np.logical_and(exc_morning, exc_afternoon)].copy()
        ret = ret.loc[np.logical_and(exc_morning, exc_afternoon)].copy()
        
        amt_per_deal = amt/dealnum
        amt_per_deal_threshold = amt_per_deal.quantile(1 - threshold)
        amt_per_deal_index = np.zeros(amt_per_deal.shape)
        amt_per_deal_index[(amt_per_deal.values - amt_per_deal_threshold.values) > 0] = 1
        ret_big_order = pd.DataFrame((ret.values * amt_per_deal_index + 1), index=ret.index, columns=ret.columns)
        ans = (ret_big_order.prod(axis=0) - 1) * 100
        ans[ans.values == 0] = np.nan
        return -ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。

