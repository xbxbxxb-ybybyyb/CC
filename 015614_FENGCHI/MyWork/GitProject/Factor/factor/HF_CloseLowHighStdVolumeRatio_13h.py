from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_CloseLowHighStdVolumeRatio_13h(BaseFactor):
    """
    * 因子名：HF_CloseLowHighStdVolumeRatio_13h
    * 因子功能描述：T-1日下午盘到T日Close滚动波动率低高分位数时刻成交量之比，值越大，说明低波动时刻成交活跃，未来越容易上涨
    * 因子参数：MinuteClose,MinuteVolume
    * 作者：游加平
    * 因子创建日期： 2019.9.24
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_adj_minute","FactorData.Basic_factor.volume_adj_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window = 20


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_adj_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_adj_minute']
        
        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]
        
        close = MinuteClose.loc[pre_date].iloc[-120:].append(MinuteClose.loc[compute_date])
        volume = MinuteVolume.loc[pre_date].iloc[-120:].append(MinuteVolume.loc[compute_date])
        rolling_std = self.rolling_std(close,window=10)

        arr = rolling_std.values > np.nanquantile(rolling_std.values,0.9,axis=0)
        top = pd.DataFrame(arr,index=rolling_std.index,columns=rolling_std.columns)
        arr = rolling_std.values < np.nanquantile(rolling_std.values,0.1,axis=0)
        tail = pd.DataFrame(arr,index=rolling_std.index,columns=rolling_std.columns)

        # top = (rolling_std > rolling_std.quantile(0.9))
        # tail = (rolling_std < rolling_std.quantile(0.1))
        ratio_top = volume[top].sum() / volume.sum()
        ratio_tail = volume[tail].sum() / volume.sum()
        return ratio_tail / ratio_top

    def rolling_max(self,factor,window):
        return factor.rolling(window=window,min_periods=1).max()

    def rolling_std(self,factor,window):
        return factor.rolling(window=window,min_periods=1).std() 

    def reform(self, factor):
        factor = factor / self.rolling_max(factor,window=self.reform_window)
        factor.fillna(0.,inplace=True)
        return factor
