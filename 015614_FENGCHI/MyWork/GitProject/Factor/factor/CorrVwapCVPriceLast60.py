from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import pandas as pd
import numpy as np
import copy
from collections import Counter
class CorrVwapCVPriceLast60(BaseFactor):

    """
    *因子名：CorrVwapCVPriceLast60_13h
    *因子功能描述：当日10:30-11:30，5分钟vwap与5分钟vwap的变异系数的相关性,与前五天该值的均值相加。变异系数=vwap标准差/vwap均值
    相关性越低，说明价格低时价格相对波动更剧烈，有反弹趋势。
    *因子参数：[MinuteTurnover]: 分钟成交额
               [MinuteVolume]: 分钟成交量

    *作者：周璇
    *因子创建日期：2019.8.26
    *函数修改日期：尚未修改
    *修改人：尚未修改
    *修改原因：尚未修改
    """

    factor_type = "FIX"
    s_amt_min = 'FactorData.Basic_factor.amt_minute'
    s_vol_min = 'FactorData.Basic_factor.volume_minute'
    depend_data = [s_amt_min, s_vol_min]
    n = 5
    minute_lag = n
    # def definition(self, MinuteTurnover,MinuteVolume):
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        amt_min = database.depend_data[self.s_amt_min]
        vol_min = database.depend_data[self.s_vol_min]
        CorrVwapCVPriceLast60 = self.minute(amt_min, vol_min)
        return -CorrVwapCVPriceLast60


    def minute(self, MinuteTurnover,MinuteVolume):
        fmt = '%Y-%m-%d'
        datelist = sorted(np.unique(MinuteVolume.index.strftime(fmt)))
        CorrVwapCVPriceLast60 = pd.DataFrame(index=[pd.Timestamp(date) for date in datelist],columns=MinuteVolume.columns)
        for date in datelist:
            vwap = MinuteTurnover.loc[date]/MinuteVolume.loc[date]
            vwap_mean = vwap.rolling(window=5,min_periods=4).mean()
            vwap_std = vwap.rolling(window=5,min_periods=4).std()
            vwap_cv = vwap_std/vwap_mean
            if date==datelist[-1]:
                CorrVwapCVPriceLast60.loc[date] = Util.array_coef(vwap_cv.iloc[-60:], vwap_mean.iloc[-60:])
            else:
                CorrVwapCVPriceLast60.loc[date] = Util.array_coef(vwap_cv, vwap_mean)
        result = CorrVwapCVPriceLast60.iloc[:-1].rolling(window=5,min_periods=4).mean().iloc[-1]+CorrVwapCVPriceLast60.iloc[-1]
        return result