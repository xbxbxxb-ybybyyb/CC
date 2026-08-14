# -*- coding: utf-8 -*-
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_AmtStdStrengthCloseChange_13h(BaseFactor):
    """
    *因子名 : HF_AmtStdStrengthCloseChange_13h
    *因子功能描述 : 成交额波动率与收盘价的相关性,取偏离值;值越大，表示放量超买，收益越低
    *因子参数 : MinuteClose-分钟收盘价，MinuteTurnover-分钟成交额
    *作者 : hezq
    *因子创建日期 : 2019.08.02
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5    

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        amt_today = MinuteTurnover.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        
        amt_std = amt_today.rolling(window=5,min_periods=1).std()
        res = Util.array_coef(close,amt_std)
        return res

    def reform(self, df):
        df[np.isinf(df)] = np.nan
        df = df-df.shift(self.reform_window).fillna(0)
        return -df