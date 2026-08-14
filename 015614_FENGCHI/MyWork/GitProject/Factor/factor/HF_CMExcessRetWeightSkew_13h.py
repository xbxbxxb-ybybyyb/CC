from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform

class HF_CMExcessRetWeightSkew_13h(BaseFactor):
    """
    * 因子名：HF_CMExcessRetWeightSkew_13h
    * 因子功能描述：T日Close相对全市场超额筹码收益率的时间加权偏度，取5日指数加权平均值
    * 因子参数：MinuteClose
    * 作者：游加平
    * 因子创建日期： 2019.10.22
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 5

    def definition(self,MinuteClose):
        factor = self.minute_help(self.minute,'MinuteValidHelp',MinuteClose)
        factor = self.rolling_ewm(factor,window=5)
        factor[np.isnan(factor).all(axis=1)] = 0.
        return factor

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]

        close = MinuteClose.loc[compute_date]

        arr = close.iloc[-1].values / close.values - 1.0
        ret = pd.DataFrame(arr,index=close.index,columns=close.columns)

        # ret = close.iloc[-1] / close - 1.0
        ret = ret.sub(ret.mean(axis=1),axis=0)        
        ret_skew = ret.groupby(pd.Grouper(freq='30min')).skew().dropna(axis=0,how='all')
        weight = np.arange(1,ret_skew.shape[0] + 1)
        skew = ret_skew.multiply(weight,axis=0).sum()        
        return skew

    def rolling_ewm(self,factor,window):
        def ewm(x):
            window=len(x)
            weight = np.array( [(1-(2.0/(window+1))) ** (window-i) for i in range(1, window + 1)] )
            return np.nansum(x * weight) / np.sum(weight)
        factor = factor.rolling(window=window).apply(lambda x:ewm(x))
        return factor

    def reform(self, factor):
        # 计算n日波动率
        factor = self.rolling_ewm(factor,window=self.reform_window)
        factor[np.isnan(factor).all(axis=1)] = 0.
        return factor        