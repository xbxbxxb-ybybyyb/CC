from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
from xfactor.FixUtil import minute_data_transform

class MinAmtKurt20d(BaseFactor):
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20
    def calc_single(self, database):
        MinuteTurnover = database.depend_data["FactorData.Basic_factor.amt_minute"]
        amt = MinuteTurnover.resample('20min').sum().dropna(how='all', axis=0)
        amt = amt.div(amt.sum(axis=1), axis=0)
        return -amt.kurt()
    def reform(self,temp_result):
        return temp_result.fillna(0).rolling(20,1).sum()