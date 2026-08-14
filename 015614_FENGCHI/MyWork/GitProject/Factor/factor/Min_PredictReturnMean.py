# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class Min_PredictReturnMean(BaseFactor):
    """
    *因子名 : Min_PredictReturnMean
    *因子功能描述 :收盘前30分钟，利用收益率乘上成交量的增长，表示放量涨还是放量跌的状态，取其均值
    *因子参数 :  MinuteClose-分钟收盘价，MinuteVolume-分钟交易量
    *作者 : hezq
    *因子创建日期 : 2019.05.09
    """
    factor_type = "DAY"
    # fix_times = ["1500"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.close_minute"]
    lag = 0
    reform_window = 5

    # def definition(self,MinuteClose,MinuteVolume):
    #     up_var = self.minute_help(self.minute,'Min_PredictReturnMeanHelp',MinuteClose,MinuteVolume)
    #     up_var = up_var.rolling(window=5,min_periods=1).mean()
    #     return up_var

    # def minute(self,MinuteClose,MinuteVolume): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     res_ = {}
    #     for date in date_list:
    #         dt = pd.Timestamp(date)
    #         Close = MinuteClose.loc[date].sort_index()
    #         Volume = MinuteVolume.loc[date].sort_index()
    #         res = (Volume/(Volume.shift(1)))* (Close/Close.shift(1)-1)
    #         res[np.isinf(res)]=np.nan
    #         res = res.iloc[-30:,:].sum(axis=0)
    #         res[Volume.iloc[-30:,:].sum(axis=0)==0]=np.nan
    #         res_[dt] = res
    #     res_ = pd.DataFrame(res_).T
    #     res_ = res_.loc[:,MinuteClose.columns]
    #     return -res_

    def calc_single(self, database):
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        res_ = {}
        for date in date_list:
            dt = pd.Timestamp(date)
            Close = MinuteClose.loc[date].sort_index()
            Volume = MinuteVolume.loc[date].sort_index()
            # res = (Volume/(Volume.shift(1)))* (Close/Close.shift(1)-1)
            res = (Volume/(Volume.shift(1)))* (Close.pct_change(1))
            res[np.isinf(res)]=np.nan
            res = res.iloc[-30:,:].sum(axis=0)
            res[Volume.iloc[-30:,:].sum(axis=0)==0]=np.nan
            # res_[dt] = res
        # res_ = pd.DataFrame(res_).T
        # res_ = res_.loc[:,MinuteClose.columns]
        return -res

    def reform(self, result):
        result = result.rolling(window=5,min_periods=1).mean()
        return result 