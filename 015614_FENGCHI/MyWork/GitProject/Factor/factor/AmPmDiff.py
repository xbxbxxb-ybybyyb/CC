from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import copy

class AmPmDiff(BaseFactor):
    """
    """
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.open"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0

    reform_window = 100

    def calc_single(self, database):
        close_badj = database.depend_data['FactorData.Basic_factor.close']
        open_badj = database.depend_data['FactorData.Basic_factor.open']
        alpha = (close_badj - open_badj)/open_badj        
        return alpha.iloc[-1]
    def  reform(self, temp_result):
        A = -temp_result.rolling(self.reform_window,min_periods=5).mean()/temp_result.rolling(self.reform_window,min_periods=5).std()
        return A


