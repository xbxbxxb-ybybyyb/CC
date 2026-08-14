from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_LowReBiasSelfCorrStable_13h(BaseFactor):

    """
    * 因子名：HF_LowReBiasSelfCorrStable_13h
    * 因子功能描述：个股收益相对全市场的bias在时序上的自相关性，自相关性越高，说明异常收益持续性高，不宜投资；反之亦然。
    * 将该值剔除五日波动率，求得在日级别，异常持续的现象，将该值作为因子。
    * 因子参数：MinuteOpen, MinuteClose
    * 因子创建日期：20190805
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
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
        
        return_df = (close_df / open_df).values - 1
        return_df = pd.DataFrame(return_df,index=close_df.index,columns=close_df.columns)

        mkt_mean_return = return_df.mean(axis = 1)
        res_return = return_df.subtract(mkt_mean_return, axis = 'index')
        res_corr = Util.array_coef(res_return,res_return.shift(1))
        
        return res_corr

    def reform(self, factor):
        result = -factor/factor.rolling(5).std()
        return result    