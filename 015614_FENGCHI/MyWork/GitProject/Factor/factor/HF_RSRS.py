# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_RSRS(BaseFactor):
    """
    *因子名 : HF_RSRS_13h
    *因子功能描述 : 相对阻力支撑强度指标，High相对Low回归得到的beta作为因子值，值越大，买入越强度越大，次日收益越低。
    *因子参数 : MinuteHigh-分钟最高价，MinuteLow-分钟最低价
    *作者 : hezq
    *因子创建日期 : 2019.6.21

    """

    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = [ "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.high_minute"]
    lag = 0

    # def definition(self,MinuteHigh,MinuteLow):
    #     df = self.minute_help(self.minute, 'HF_RSRS_13hHelp',MinuteHigh,MinuteLow)
    #     df[np.isinf(df)] = np.nan
    #     return -df
    # def minute(self,MinuteHigh,MinuteLow): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteHigh.index.strftime(fmt))[-1]
    #     # print(date_list)
    #     high = MinuteHigh.sort_index(ascending=True)
    #     low = MinuteLow.sort_index(ascending=True)
    #     res = high.std(axis=0)/low.std(axis=0)*(high.corrwith(low))
    #     return res

    def calc_single(self, database):
        MinuteLow = database.depend_data["FactorData.Basic_factor.low_minute"]
        MinuteHigh = database.depend_data["FactorData.Basic_factor.high_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteHigh.index.strftime(fmt))[-1]
        # print(date_list)
        high = MinuteHigh.sort_index(ascending=True)
        low = MinuteLow.sort_index(ascending=True)
        # res = high.std(axis=0)/low.std(axis=0)*(high.corrwith(low))
        res = high.std(axis=0)/low.std(axis=0)*(Util.array_coef(high,low))
        return -res
