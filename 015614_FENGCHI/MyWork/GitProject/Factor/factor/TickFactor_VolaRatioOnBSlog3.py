from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
from xfactor.Util import data_filter


class TickFactor_VolaRatioOnBSlog3(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # fix_times = ["1000", "1030",'1100','1300','1330','1400','1430']
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.buytradeamt_minute',
                   'FactorData.Basic_factor.selltradeamt_minute',
                   'FactorData.Basic_factor.close_minute',
                   'FactorData.Basic_factor.limit_status_minute',]
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 3

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        period = '5min'
        minute_data_transform(database.depend_data,['drop1','drop4'])
        limit_status = database.depend_data["FactorData.Basic_factor.limit_status_minute"].copy()
        close = database.depend_data["FactorData.Basic_factor.close_minute"].copy()
        close = data_filter(close,limit_status,method='minute')
        ret = np.log(close/close.shift(1))
        ret.iloc[237,:] = np.nan
        filter_index = close.iloc[-237*self.lag:, :].resample(period, how='last').dropna(axis=0,how='all').index
         
        b_amt = database.depend_data["FactorData.Basic_factor.buytradeamt_minute"].copy().iloc[-237*self.lag:,:]
        s_amt = database.depend_data["FactorData.Basic_factor.selltradeamt_minute"].copy().iloc[-237*self.lag:,:]

        b_amt = data_filter(b_amt,limit_status,method='minute')
        s_amt = data_filter(s_amt,limit_status,method='minute')

        b_amt_min = b_amt.resample(period).sum().reindex(filter_index)
        s_amt_min = s_amt.resample(period).sum().reindex(filter_index)
        ret_min = ret.resample(period).sum().reindex(filter_index)
        b_greater = (b_amt_min-s_amt_min).values > 0
        s_greater = (b_amt_min-s_amt_min).values < 0
        vola = pd.DataFrame(ret_min.values**2,index=ret_min.index,columns=ret_min.columns)
        vola_b = vola * b_greater / b_greater
        vola_s = vola * s_greater / s_greater
        ans = vola_b.mean()/vola_s.mean()
        ans[ans == 0] = np.nan
        return np.log(ans)


    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        alpha = temp_result.rolling(self.reform_window,min_periods=int(self.reform_window/2)).mean()
        return alpha
