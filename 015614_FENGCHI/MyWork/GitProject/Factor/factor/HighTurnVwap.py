# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class HighTurnVwap(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.volume_adj_minute","FactorData.Basic_factor.float_a_shares"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    minute_lag = 1
    lag = 5
    # fix_times=["1300"]
    def calc_single(self, database):
        data_min = {"FactorData.Basic_factor.amt_minute":database.depend_data['FactorData.Basic_factor.amt_minute'],
                   "FactorData.Basic_factor.volume_adj_minute":database.depend_data['FactorData.Basic_factor.volume_adj_minute']}
        minute_data_transform(data_min, operation = ['drop', 'merge'])
        MinuteTurnover = data_min['FactorData.Basic_factor.amt_minute']
        MinuteVolume = data_min['FactorData.Basic_factor.volume_adj_minute']
        float_a_shares = database.depend_data["FactorData.Basic_factor.float_a_shares"]
        df_single_day = self.minute_help( MinuteTurnover, MinuteVolume,float_a_shares)
        return df_single_day
    def div_df_series(self,df,series):
        return pd.DataFrame(df.values/series.values,index=df.index,columns=df.columns)
    def minute_help(self, MinuteTurnover,MinuteVolume, float_a_shares):
        date_list = sorted(np.unique(MinuteVolume.index.strftime('%Y%m%d')))
        date = date_list[-1]
        pre_date = date_list[-2]
        float_a_shares_yesterday = float_a_shares.loc[pre_date]
        turn = self.div_df_series(MinuteVolume,float_a_shares_yesterday)

        vwap = MinuteTurnover.where(turn.rank(pct=True).values > 0.9).sum()/MinuteVolume.where(turn.rank(pct=True).values > 0.9).sum()
        f = -vwap/(MinuteTurnover.sum()/MinuteVolume.sum())
        return f