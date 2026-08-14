from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_LDeg1_13h(BaseFactor):
    """
    *因子名 : HF_LDeg1_13h
    *因子功能描述 : 收盘价相对最低价的回归系数；值越大，表示卖出力量越强，未来收盘价格越高，收益越低
    *因子参数 : MinuteClose-分钟收盘价,MinuteLow-分钟最低价
    *作者 : hezq
    *因子创建日期 : 2019.7.16

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 60

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        low = MinuteLow.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        res_corr = Util.array_coef(low.shift(1),close)
        res = res_corr*close.std(axis=0)/low.shift(1).std(axis=0)
        return res
    def reform(self, df):
        df = (df-df.rolling(window=self.reform_window,min_periods=1).mean())\
        /df.rolling(window=self.reform_window,min_periods=1).std()
        df[np.isinf(df)] = np.nan
        return -df    