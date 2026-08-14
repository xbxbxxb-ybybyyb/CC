from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_IlliqShortcut_13h(BaseFactor):
    """
    *因子名 : HF_IlliqShortcut_13h
    *因子功能描述 : 分钟级非流动性指标，用交易额推动价格的最短路径来衡量。
    *因子参数 : MinuteHigh-分钟最高价,MinuteLow-分钟最低价,MinuteOpen-分钟开盘价,MinuteClose-分钟收盘价，MinuteTrunover-分钟成交额
    *作者 : hezq
    *因子创建日期 : 2019.6.21

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute",\
    "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']  
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']  
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']  
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']  

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[-1]
        # print(date_list)
        close = MinuteClose.sort_index(ascending=True)
        high = MinuteHigh.sort_index(ascending=True)
        low = MinuteLow.sort_index(ascending=True)
        open_ = MinuteOpen.sort_index(ascending=True)
        min_amt = MinuteTurnover.sort_index(ascending=True)
        
        shortcut=(high-low)+(high-low)-abs(open_-close)
        arr = min_amt.values==0
        arr_df = pd.DataFrame(arr,index=min_amt.index,columns=min_amt.columns)
        
        min_amt[arr_df] = np.nan
        illiq = (shortcut/min_amt).values*1000000
        illiq = pd.DataFrame(illiq,index=shortcut.index,columns=shortcut.columns)
        res = illiq.sum(axis=0)
        res[np.isinf(res)] = np.nan
        return res
