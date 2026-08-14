from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class GTJA1_6(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.open_minute","FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.open","FactorData.Basic_factor.close","FactorData.Basic_factor.volume_by_share","FactorData.Basic_factor.adjfactor","FactorData.Basic_factor.limit_status_minute","FactorData.Basic_factor.Data_limit_pctg"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=6
    reform_window=1

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        limit_pctg = database.depend_data['FactorData.Basic_factor.Data_limit_pctg'].astype('float64')

        def arraycoef(x, y):
            delta_x = x - np.nanmean(x, axis=0)
            delta_y = y - np.nanmean(y, axis=0)
            multi = np.nanmean(delta_x * delta_y, axis=0) / (np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
            multi[np.isinf(multi)] = np.nan
            return multi

        # 播放的数据通过database.depend_data字典获取
        minute_close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        lstdt = [i for i in minute_close.index if i.date() == minute_close.index[-1].date()]
        minute_close = min_forward_adj(minute_close)
        minute_close = minute_close.loc[lstdt]
        minute_open = data_filter(database.depend_data['FactorData.Basic_factor.open_minute'],limit_status,method='minute')
        minute_open = min_forward_adj(minute_open)
        minute_open = minute_open.loc[lstdt]
        minute_volume = data_filter(database.depend_data['FactorData.Basic_factor.volume_minute'],limit_status,method='minute')
        minute_volume = minute_volume.loc[lstdt]

        day_close = database.depend_data["FactorData.Basic_factor.close"]
        day_open = database.depend_data['FactorData.Basic_factor.open']
        day_volume = database.depend_data['FactorData.Basic_factor.volume_by_share']
        adj_factor = database.depend_data['FactorData.Basic_factor.adjfactor']
        day_volume = data_filter(day_volume, limit_pctg, method='day')
        day_close = data_filter(day_close, limit_pctg, method='day')
        day_open = data_filter(day_open, limit_pctg, method='day')
        day_close = adj_factor*day_close
        day_open = adj_factor*day_open
        day_delta = (day_volume - day_volume.shift(1)).rank(axis=1).iloc[1:,:].values
        day_rate = ((day_close - day_open)/day_open).rank(axis=1).iloc[1:,:].values

        minute_delta = (minute_volume.sum() - day_volume.iloc[-1,:]).rank().values.reshape(1,day_delta.shape[1])
        minute_rate = ((minute_close.iloc[-1,:] - minute_open.iloc[0,:]) / minute_open.iloc[0,:]).rank().values.reshape(1,day_delta.shape[1])

        delta = np.concatenate((day_delta, minute_delta), axis=0)
        rate = np.concatenate((day_rate, minute_rate), axis=0)
        ans_df = arraycoef(delta, rate)

        current_date = minute_close.index[-1].strftime('%Y-%m-%d')
        df_factor = pd.DataFrame(index=[pd.Timestamp(current_date)], columns=minute_close.columns)
        df_factor.loc[current_date,:] = ans_df
        return df_factor.iloc[0,:]

    def reform(self, temp_result):
        #数据通过self.data_base字典获取

        factor_values = temp_result  # 传入这里的函数每天都会调用一次播放数据计算中间量
        factor_values = factor_values.rolling(window=self.reform_window, min_periods=1).mean()
        return factor_values


