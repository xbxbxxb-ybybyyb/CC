from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_Hl2OStrength_13h(BaseFactor):
    """
    *因子名 : HL_Hl2OStrength_13h
    *因子功能描述 : 最高价减最低价表示买卖力量差额，与收盘价的未来收益率的相关系数；值越大，买卖力度与收益率同向运动，收益越高
    *因子参数 : MinuteClose-分钟收盘价
    *作者 : hezq
    *因子创建日期 : 2019.7.16

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute",\
    "FactorData.Basic_factor.low_minute", "FactorData.Basic_factor.open_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 60


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']  
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']  
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']  

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        open_ = MinuteOpen.sort_index(ascending=True)
        low = MinuteLow.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        high = MinuteHigh.sort_index(ascending=True)

        arr = close.values/close.shift(1).values-1
        df = pd.DataFrame(arr*100,index=close.index,columns=close.columns)

        re1 = (df).shift(-2)
        data =(((high-low)/open_).values-1)*100         
        re2 = pd.DataFrame(data,index=high.index,columns=high.columns)
        res_corr = Util.array_coef(re1,re2)
        return res_corr
    def reform(self, df):
        df = (df-df.rolling(window=self.reform_window,min_periods=1).mean())\
        /df.rolling(window=self.reform_window,min_periods=1).std()
        df[np.isinf(df)] = np.nan        
        return df  