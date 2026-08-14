# -*- coding: utf-8 -*-
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class HF_OverBuy(BaseFactor):
    """
    *因子名 : HF_OverBuy_13h
    *因子功能描述 : 分钟收盘价超越2倍标准差的相对幅度，超出向上幅度之和；值越大，发生反转的可能性越大，即收益越低
    *因子参数 : MinuteClose-分钟收盘价
    *作者 : hezq
    *因子创建日期 : 2019.6.21

    """
    factor_type = "FIX"
    # fix_times = ["1300"]
    # depend_factors = ["SampleFactor"]
    depend_data = ["FactorData.Basic_factor.volume_minute", "FactorData.Basic_factor.low_minute", 
    "FactorData.Basic_factor.amt_minute","FactorData.Basic_factor.close_minute"]
    lag = 0

    # def definition(self, MinuteClose):
    #     df = self.minute_help(self.minute, 'HF_OverBuy_13hHelp', MinuteClose)
    #     df[np.isinf(df)] = np.nan
    #     return -df

    # def minute(self,MinuteClose): 
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
    #     # print(date_list)
    #     close = MinuteClose.loc[date_list].sort_index(ascending=True)
    #     mean_close = close.rolling(window=10,min_periods=1).mean()
    #     std_close = close.rolling(window=10,min_periods=1).std()
    #     boll_up = mean_close+2*std_close
    #     up_range = close-boll_up
    #     uprange_pct = (up_range[up_range>0]/boll_up) 
    #     res = uprange_pct.sum(axis=0)[uprange_pct.mean(axis=0).notnull()]
    #     res = res.reindex(index=close.columns)
    #     return res

    def calc_single(self, database):
        MinuteLow = database.depend_data["FactorData.Basic_factor.low_minute"]
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        MinuteVolume = database.depend_data["FactorData.Basic_factor.volume_minute"]
        MinuteClose = database.depend_data["FactorData.Basic_factor.close_minute"]
        minute_data_transform(database.depend_data, operation = ['drop', 'merge'])

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        close = MinuteClose.loc[date_list].sort_index(ascending=True)
        mean_close = close.rolling(window=10,min_periods=1).mean()
        std_close = close.rolling(window=10,min_periods=1).std()
        # boll_up = mean_close+2*std_close
        boll_up = pd.DataFrame(mean_close.values+2*std_close.values,
            index=mean_close.index, columns=mean_close.columns)
        up_range = close-boll_up
        # uprange_pct = (up_range[up_range>0]/boll_up) 
        uprange_pct = (up_range[pd.DataFrame(up_range.values>0,
            index=up_range.index, columns=up_range.columns)]/boll_up) 
        res = uprange_pct.sum(axis=0)[uprange_pct.mean(axis=0).notnull()]
        res = res.reindex(index=close.columns)
        return -res
