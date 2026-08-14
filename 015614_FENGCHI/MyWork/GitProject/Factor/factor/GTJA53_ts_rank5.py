from xfactor.Util import *
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj


class GTJA53_ts_rank5(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute",'FactorData.Basic_factor.adjfactor',"FactorData.Basic_factor.close","FactorData.Basic_factor.limit_status_minute","FactorData.Basic_factor.Data_limit_pctg"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag=12
    reform_window=5
    ptype='ts_rank'

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        #分钟线242转换为240或者241根，operation为list，默认为["merge", "merge"],第一位表示对925时刻处理，第二位表示对1500处理
        #处理方式可分为"merge"、"drop"和"",分别表示合并、删除、和不操作。优化后单次播放时分钟线转换速度为毫秒级
        minute_data_transform(database.depend_data, operation = ["drop1", "drop4"])
        limit_status = database.depend_data['FactorData.Basic_factor.limit_status_minute']
        limit_pctg = database.depend_data['FactorData.Basic_factor.Data_limit_pctg'].astype('float64')

        # 播放的数据通过database.depend_data字典获取
        minute_close = data_filter(database.depend_data['FactorData.Basic_factor.close_minute'],limit_status,method='minute')
        lstdt = [i for i in minute_close.index if i.date() == minute_close.index[-1].date()]
        minute_close = minute_close.loc[lstdt,:]
        minute_close = min_forward_adj(minute_close)
        current_date = minute_close.index[-1].strftime('%Y-%m-%d')
        adj_factor = database.depend_data['FactorData.Basic_factor.adjfactor'].copy()
        day_close = database.depend_data['FactorData.Basic_factor.close'].copy()*adj_factor
        day_close = data_filter(day_close, limit_pctg, method='day')
        day_close.loc[pd.Timestamp(current_date), :] = minute_close.iloc[-1, :]

        ans_df = day_close - day_close.shift(1)
        ans_df = ans_df.iloc[1:,:]
        ans_df[ans_df>0] = 1
        ans_df[ans_df<=0] = 0
        ans_df = ans_df.sum(axis=0) / 12 * 100


        df_factor = pd.DataFrame(index=[pd.Timestamp(current_date)], columns=minute_close.columns)
        df_factor.loc[current_date,:] = ans_df
        return df_factor.iloc[0,:]

    def reform(self, temp_result):
        
        def rank(array):
            s = pd.Series(array)
            return s.rank()[len(s) - 1]
        factor_values = temp_result  # 传入这里的函数每天都会调用一次播放数据计算中间量
        if self.ptype == None:
            ans_df = factor_values
        elif self.ptype == 'bias':
            mean = factor_values.rolling(window=self.reform_window, min_periods=1).mean()
            ans_df = factor_values - mean
        elif self.ptype == 'ts_rank':
            ans_df = factor_values.rolling(window=self.reform_window, min_periods=1).apply(func=rank)
        return ans_df


