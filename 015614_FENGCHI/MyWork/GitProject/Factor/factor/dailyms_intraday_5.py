from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform,min_forward_adj
import statsmodels.api as sm
from copy import deepcopy
import pandas as pd

class dailyms_intraday_5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag =4
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        close_adj=min_forward_adj(close)
        ret=pd.DataFrame(close_adj.values / close_adj.shift(1).values - 1, index=close_adj.index,
                     columns=close_adj.columns)
        ret = data_filter(ret,limit_status,method='minute')
        database.depend_data['FactorData.Basic_factor.ret_minute'] = ret
        minute_data_transform(database.depend_data, operation=["drop1", "drop4"])


        ret_adj = database.depend_data['FactorData.Basic_factor.ret_minute'].copy()
        date = pd.Series([i.date() for i in ret_adj.index], index=ret_adj.index)
        daily_retmean = ret_adj.groupby(date).mean()
        daily_retstd = ret_adj.groupby(date).std()

        ret_mean = pd.Series(np.nanmean(daily_retmean.values, axis=0), index=daily_retmean.columns)
        ret_std = pd.Series(np.nanstd(daily_retstd.values, axis=0), index=daily_retstd.columns)
        ret_ms = pd.Series(ret_mean.values / ret_std.values, index=ret_mean.index)
        ret_ms[pd.Series(abs(ret_std.values / ret_mean.values), index=ret_mean.index) < 0.00001] = np.nan
        return ret_ms


