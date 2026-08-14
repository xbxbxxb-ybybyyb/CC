from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform
import copy

class DownSpeed(BaseFactor):
    """
    """
    factor_type = "DAY"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1

    reform_window = 10

    def calc_single(self, database):

        def func_max(x):
            if x.sum() == 0:
                y = np.nan
            else:
                y = list(x).index(x.max())
            return y   

        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']        


        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]

        Close = MinuteClose.loc[compute_date]
        length = len(Close)

        loc_max = Close.apply(func_max)
        aroon_up = (length - loc_max)/length
        ret_min = (Close.iloc[-1]-Close.max())/Close.max()
        ret_speed_down = ret_min/aroon_up # 收益率相对下降速度
        ret_speed_down[np.isinf(ret_speed_down)] = np.nan
        
        return ret_speed_down

    def reform(self, up_var):
        # 计算n日波动率
        up_var = -(up_var.rolling(window=self.reform_window).mean())/up_var.rolling(window=self.reform_window).std()
         
        return up_var       
 
