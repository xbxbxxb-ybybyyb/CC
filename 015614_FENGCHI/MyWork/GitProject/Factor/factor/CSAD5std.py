from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.Util import *
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class CSAD5std(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.limit_status_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=1
    reform_window=5
    num_of_stock=10
    period=30
    process='std'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["", ""])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        close = database.depend_data['FactorData.Basic_factor.close_minute']
        close =data_filter(close,limit_status, method='minute')

        close =min_forward_adj(close)
        close = close.iloc[-237*(self.lag):, :].copy()
        volume = database.depend_data['FactorData.Basic_factor.volume_minute']
        volume = data_filter(volume,limit_status, method='day')
        volume.iloc[-237*(self.lag):, :].copy()
        volume_day = volume.resample('1D').sum().iloc[-1, :].copy()
        ret = np.log(close/close.shift(1))
        period = str(self.period) + 'min'
        ret_min = ret.resample(period).sum()
        ret_min_bench = ret.resample(period,how='max').dropna(how='all')
        ret_min = ret_min.reindex(ret_min_bench.index)
        ret_total = ret_min.sum()
        cor = ret_min.corr()
        np.fill_diagonal(cor.values,0)
        quantile = 1 - (self.num_of_stock)/(volume_day.values != 0).sum()
        threshold = cor.quantile(quantile)
        degree_num0 = np.zeros(cor.shape)
        degree_num0[cor.values - threshold.values >=0 ] = 1
        ret_df = (np.ones(cor.shape)*ret_total.values).T
        ret_diff_abs = pd.DataFrame(abs(ret_df - ret_total.values)*degree_num0/degree_num0,index=cor.index,columns=cor.columns)
        casd = ret_diff_abs.mean()
        ans = casd * volume_day / volume_day
        return ans


    def reform(self, temp_result):
        
        casd = temp_result
        if self.process == 'mean':
            alpha = casd.rolling(self.reform_window,min_periods=int(self.reform_window/2)).mean()
        elif self.process == 'std':
            alpha = casd.rolling(self.reform_window,min_periods=int(self.reform_window/2)).std()
        return alpha

