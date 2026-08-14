from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class GTJA8(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute","FactorData.Basic_factor.low_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.high","FactorData.Basic_factor.vwap","FactorData.Basic_factor.low","FactorData.Basic_factor.limit_status_minute","FactorData.Basic_factor.Data_limit_pctg"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=4
    reform_window=1
    ptype=None

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        limit_pctg = database.depend_data['FactorData.Basic_factor.Data_limit_pctg'].astype('float64')

        # 播放的数据通过database.depend_data字典获取
        min_high = data_filter(database.depend_data['FactorData.Basic_factor.high_minute'],limit_status,method='minute')
        min_high = min_forward_adj(min_high)
        lstdt = [i for i in min_high.index if i.date() == min_high.index[-1].date()]
        min_high = min_high.loc[lstdt,:]
        min_low = data_filter(database.depend_data["FactorData.Basic_factor.low_minute"],limit_status,method='minute')
        min_low = min_forward_adj(min_low)
        min_low = min_low.loc[lstdt,:]
        current_date = min_high.index[-1].strftime('%Y-%m-%d')
        min_volume = data_filter(database.depend_data["FactorData.Basic_factor.volume_minute"],limit_status,method='minute')
        min_volume = min_volume.loc[lstdt, :]
        min_amt = data_filter(database.depend_data["FactorData.Basic_factor.amt_minute"],limit_status,method='minute')
        min_amt = min_amt.loc[lstdt, :]

        adjfactor = database.depend_data["FactorData.Basic_factor.adjfactor"].copy()
        high = database.depend_data["FactorData.Basic_factor.high"].copy()
        high = data_filter(high, limit_pctg, method='day')
        high = high*adjfactor
        low = database.depend_data["FactorData.Basic_factor.low"].copy()
        low = data_filter(low, limit_pctg, method='day')
        low = low*adjfactor
        vwap = database.depend_data["FactorData.Basic_factor.vwap"].copy()
        vwap = data_filter(vwap, limit_pctg, method='day')
        vwap = vwap*adjfactor
        
        high.loc[pd.Timestamp(current_date), :] = min_high.max(axis=0)
        low.loc[pd.Timestamp(current_date), :] = min_low.min(axis=0)
        vwap.loc[pd.Timestamp(current_date), :] = min_forward_adj(min_amt.sum(axis=0) / min_volume.sum(axis=0), pd.Timestamp(current_date))
        vwap = vwap.replace({np.inf: np.nan})

        temp1 = (high.values + low.values) / 2 * 0.2
        temp1 = temp1[-1,:] - temp1[0,:]
        temp2 = vwap.values * 0.8
        temp2 = temp2[-1,:] - temp2[0,:]
        ans = (temp1 + temp2) * -1
        ans_df = pd.Series(ans, index=min_high.columns)
        ans_df = ans_df.rank()
        return ans_df

    def reform(self, temp_result):
        
        def rank(array):
            s = pd.Series(array)
            return s.rank()[len(s) - 1]
        factor_values = temp_result  # 传入这里的函数每天都会调用一次播放数据计算中间量
        if self.ptype == None:
            ans_df = factor_values
        elif self.ptype == 'mean':
            ans_df = factor_values.rolling(window=self.reform_window, min_periods=1).mean()
        elif self.ptype == 'skew':
            ans_df = factor_values.rolling(window=self.reform_window, min_periods=1).skew()
        elif self.ptype == 'ts_rank':
            ans_df = factor_values.rolling(window=self.reform_window, min_periods=1).apply(func=rank)
        return ans_df


