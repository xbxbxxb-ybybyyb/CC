from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_AmtVolatilityPriceCorr_13h(BaseFactor):
    """
    * 因子名：HF_AmtVolatilityPriceCorr_13h
    * 因子功能描述：成交额5分钟波动率和价格的相关性，相关性越低，异常炒作越少，股票越具有投资价值
    * 因子参数：  MinuteClose,MinuteHigh,MinuteLow,MinuteVolume,MinuteTurnover
    * 因子创建日期： 20190710
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.amt_minute", "FactorData.Basic_factor.close_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 0
    
    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']        

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        compute_date = date_list[-1]
        
        close_df = MinuteClose.loc[compute_date]
        amt_df = MinuteTurnover.loc[compute_date]
        amt_volatility = amt_df.rolling(5).std()        
        res_corr = Util.array_coef(amt_volatility.iloc[5:],close_df.iloc[5:])

        return -res_corr
        
