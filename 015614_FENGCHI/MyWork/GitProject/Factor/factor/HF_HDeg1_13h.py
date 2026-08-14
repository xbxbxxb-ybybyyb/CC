from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_HDeg1_13h(BaseFactor):
    """
    *因子名 : HF_HDeg1_13h
    *因子功能描述 : 最高价相对收盘价的回归系数；值越大，最高价推动未来收盘价上涨越大，收益越高
    *因子参数 : MinuteClose-分钟收盘价,MinuteHigh-分钟最高价
    *作者 : hezq
    *因子创建日期 : 2019.7.16

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        close = MinuteClose.sort_index(ascending=True)
        high = MinuteHigh.sort_index(ascending=True)
        res_corr = Util.array_coef(high.shift(1),close)
        res = res_corr*close.std(axis=0)/high.shift(1).std(axis=0)
        res[np.isinf(res)] = np.nan
        return res
