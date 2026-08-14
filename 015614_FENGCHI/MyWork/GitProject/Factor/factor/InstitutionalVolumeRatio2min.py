# -*- coding: utf-8 -*-
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
class InstitutionalVolumeRatio2min(BaseFactor):
    # 因子频率，。默认为日频因子， 可不设置
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute","FactorData.Basic_factor.open_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    # fix_times=["1300"]
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        factor = self.minute_help(MinuteOpen, MinuteTurnover)
        return factor
    def pct_periods(self,df,window):
        return pd.DataFrame(df.values/df.shift(window).values-1,index=df.index,columns=df.columns)    
    def minute_help(self, MinuteOpen,MinuteVolume):

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteOpen.index.strftime(fmt)))
        compute_date = date_list[-1]
        open = MinuteOpen.loc[compute_date].resample('2T').last()
        volume = MinuteVolume.loc[compute_date].resample('2T').sum()
        re = self.pct_periods(open,1)
        zscore = (re - re.mean()) / re.std()
        cond = pd.DataFrame(zscore.values > 2, index=zscore.index, columns=zscore.columns)
        factor_today = -(volume[cond]).sum() / volume.sum()
        return factor_today
