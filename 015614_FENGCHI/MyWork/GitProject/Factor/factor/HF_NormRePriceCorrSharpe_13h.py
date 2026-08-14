from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_NormRePriceCorrSharpe_13h(BaseFactor):

    """
    * 因子名：HF_NormRePriceCorrSharpe_13h
    * 因子功能描述：价格与分钟线收益率在时序上取zscore，求两者相关性。相关性约小，反转效应越大。该值在5日内的稳定性作为因子。反转效应大，稳定性高，则投资收益高。
    * 因子参数： MinuteOpen, MinuteClose, MinuteHigh, MinuteLow, MinuteTurnover, MinuteVolume
    * 作者：刘道一
    * 因子创建日期： 20190721
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window = 5
    

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        
        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteOpen.index.strftime(fmt))
        compute_date = date_list[-1] 
        
        open_df = MinuteOpen.loc[compute_date]
        close_df = MinuteClose.loc[compute_date]
        
        abs_return_df = np.abs((close_df / open_df).values - 1)
        abs_return_df = pd.DataFrame(abs_return_df,index=close_df.index,columns=close_df.columns)

        mr = abs_return_df.mean(axis = 0)
        mc = close_df.mean(axis = 0)
        
        arr = (abs_return_df.values - mr.values) / (abs_return_df.std(axis = 0)).values
        normalized_abs_return = pd.DataFrame(arr,index=abs_return_df.index,columns=abs_return_df.columns)

        arr = (close_df.values - mc.values) / (close_df.std(axis = 0)).values
        normalized_close = pd.DataFrame(arr,index=close_df.index,columns=close_df.columns)
        
        result = Util.array_coef(normalized_abs_return,normalized_close)
        
        return result

    def reform(self, result):
        result = -(result-result.rolling(self.reform_window).mean())\
        /result.rolling(self.reform_window).std()
        return result             