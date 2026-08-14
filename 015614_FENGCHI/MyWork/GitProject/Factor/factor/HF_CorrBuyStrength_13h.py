from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_CorrBuyStrength_13h(BaseFactor):
    """
    *因子名 : HF_CorrBuyStrength_13h
    *因子功能描述 : 未来最高价收益率与收盘价计算的成交额的相关系数；值越来，表示成交额预测的买入力量越强，收益越高
    *因子参数 : MinuteClose-分钟收盘价，MinuteHigh-分钟最高价，MinuteVolume-分钟成交量
    *作者 : hezq
    *因子创建日期 : 2019.7.23

    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute", "FactorData.Basic_factor.volume_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 20


    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute'] 
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute'] 

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))[0]
        # print(date_list)
        volume_today = MinuteVolume.sort_index(ascending=True)
        close = MinuteClose.sort_index(ascending=True)
        high = MinuteHigh.sort_index(ascending=True)
        amt = volume_today*close
        arr = ((high/high.shift(1)).values-1)*100
        re1 = pd.DataFrame(arr,index=high.index,columns=high.columns)
        res = Util.array_coef(re1,amt.shift(2))
        return res

    def reform(self, df):
        df[np.isinf(df)] = np.nan
        df = ((df-df.rolling(window=self.reform_window,min_periods=1).mean())/df.rolling(window=self.reform_window,min_periods=1).std())
        return df