from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
class CorrWRPriceRank(BaseFactor):

    """
    *因子名：CorrWRPriceRank_13h
    *因子功能描述：当日截至13:00，分钟威廉指标的绝对值与价格的秩相关性。
    相关性越高，说明价格在低位时威廉指标偏离度不高，多空博弈更激烈，后市易上涨。
    *因子参数：[MinuteClose]: 分钟收盘价
               [MinuteHigh]: 分钟最高价
               [MinuteLow]: 分钟最低价

    *作者：周璇
    *因子创建日期：2019.7.19
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """
    factor_type = 'FIX'
    s_close_min = 'FactorData.Basic_factor.close_minute'
    s_high_min = 'FactorData.Basic_factor.high_minute'
    s_low_min = 'FactorData.Basic_factor.low_minute'
    depend_data = [s_close_min, s_high_min, s_low_min]
    minute_lag = 1

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        close_min = database.depend_data[self.s_close_min]
        high_min = database.depend_data[self.s_high_min]
        low_min = database.depend_data[self.s_low_min]
        CorrWRPrice = self.minute(close_min, high_min, low_min)
        return CorrWRPrice


    def minute(self, MinuteClose,MinuteHigh,MinuteLow):
        fmt = '%Y-%m-%d'
        datelist = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = datelist[-1]
        # pre_date = datelist[-2]
        close_min = MinuteClose.loc[compute_date]
        high_min = MinuteHigh.loc[compute_date]
        low_min = MinuteLow.loc[compute_date]
        wr = abs(2*close_min-high_min-low_min)/(high_min-low_min)
        CorrWRPrice = Util.array_coef(wr.rank(axis=0), close_min.rank(axis=0))
        return CorrWRPrice