from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_LowHighStdRatio_13h(BaseFactor):
    """
    * 因子名：HF_LowHighStdRatio_13h
    * 因子功能描述：最低价和最高价波动率之比
    * 因子参数：MinuteHigh,MinuteLow
    * 作者：游加平
    * 因子创建日期： 2019.9.19
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteHigh.index.strftime(fmt)))
        compute_date = date_list[-1]
        
        high = MinuteHigh.loc[compute_date].rolling(window=15,min_periods=1).max()
        low = MinuteLow.loc[compute_date].rolling(window=15,min_periods=1).min()
        ratio = low.std() / high.std()
        ratio.fillna(0,inplace=True)
        return ratio

