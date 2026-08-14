from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_CloseVwapSkew_13h(BaseFactor):
    """
    * 因子名：HF_CloseVwapSkew_13h
    * 因子功能描述：T日Close与滚动Vwap之差的负偏度，与5日最小值偏离度
    * 因子参数：MinuteClose,MinuteVolume,MinuteTurnover
    * 作者：游加平
    * 因子创建日期： 2019.9.23
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        compute_date = date_list[-1]

        close = MinuteClose.loc[compute_date]
        volume = MinuteVolume.loc[compute_date]
        
        arr = volume.values==0.
        volume_df = pd.DataFrame(arr,index=volume.index,columns=volume.columns)
        volume[volume_df] = np.nan

        amt = MinuteTurnover.loc[compute_date]
        vwap = amt.cumsum() / volume.cumsum()
        skew = -(close - vwap).skew()
        return skew

    def rolling_min(self,factor,window):
        return factor.rolling(window=window,min_periods=1).min()

    def reform(self, factor):
        factor = self.rolling_min(factor,window=5)
        return factor


