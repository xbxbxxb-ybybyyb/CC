from xfactor.BaseFactor import BaseFactor
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform,min_forward_adj
from xfactor.Util import data_filter

# ["FactorDailyStableRet",{'n': 20, 'Data_Base': ['play_day_minute_close'], 'play_day_lag': 20,'play_min_lag': None,
#     'generator_lag': 1,'type': 1500}, "F_D_StableRet.h5"]

class CORA_R_3(BaseFactor):
    #  定义因子参数

    # 因子频率，默认为日频因子， 可不设置
    factor_type = "FIX"
    #fix_times = ["1000", "1030",'1100','1300','1330','1400','1430']
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ['FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.close_minute','FactorData.Basic_factor.limit_status_minute']
    #依赖的个人因子库的因子，默认为空，可不设置
    depend_factors = []
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 5
    # 播放后得到的结果，可按照该长度进行rolling等计算，具体rolling方法需要在reform方法中定义。 默认为1，可不设置。
    reform_window = 3

    # 每次播放的计算具体方法。必须实现。
    def calc_single(self, database):
        minute_data_transform(database.depend_data,['drop1','drop4'])
        amt = database.depend_data["FactorData.Basic_factor.amt_minute"].copy()
        close = database.depend_data["FactorData.Basic_factor.close_minute"].copy()
        limit_status = database.depend_data["FactorData.Basic_factor.limit_status_minute"].copy()
     
        close = data_filter(min_forward_adj(close),limit_status,method='minute')
        amt = data_filter(amt,limit_status,method='minute')
        
        close_latest = close.iloc[-237:,:].copy()
        amt_latest = amt.iloc[-237:,:].copy()
        ret = abs(np.log(close_latest/close_latest.shift(1)))
        
        for i in range(int((close.shape[0]-close_latest.shape[0])/237)):
            if i == 0:
                cum_amt = amt.iloc[-237*(i+2):-237*(i+1),:].copy().values
            else:
                cum_amt = cum_amt + amt.iloc[-237*(i+2):-237*(i+1),:].copy().values
        amt_ratio = pd.DataFrame(amt_latest.values/cum_amt*19,index=amt_latest.index,columns=amt_latest.columns)
        ans = pd.Series(self.cor(amt_ratio.values,ret.shift(1).values),amt_ratio.columns)

        return ans

    # 针对播放后的结果，进行相关的rolling等操作。所用的前序数据长度应为reform_window。默认不修改temp_result， 可不重写。
    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window,min_periods=int(self.reform_window/2)).mean()

    def cor(self, x: np.array, y: np.array):
        delta_x = x - np.nanmean(x, axis=0)
        delta_y = y - np.nanmean(y, axis=0)
        corelation = np.nanmean(delta_x * delta_y, axis=0)/(np.nanstd(delta_x, axis=0) * np.nanstd(delta_y, axis=0))
        corelation[np.isinf(corelation)] = np.nan
        return corelation
