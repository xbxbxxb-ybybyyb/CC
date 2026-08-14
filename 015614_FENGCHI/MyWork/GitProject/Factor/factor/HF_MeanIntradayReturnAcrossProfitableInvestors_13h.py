from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_MeanIntradayReturnAcrossProfitableInvestors_13h(BaseFactor):

    """
    * 因子名：HF_MeanIntradayReturnAcrossProfitableInvestors_13h
    * 因子功能描述：
    *      因子含义：计算当前分钟线路径上到收盘(10h/13h/14h)时的收益，并按成交额为权重计算所有浮盈的平均收益率,将该值进行横截面中心化。
    *      浮盈值离截面中位数越小，异常炒作越少，越具有次日投资价值。
    * 因子参数：MinuteOpen, MinuteClose, MinuteTurnover
    * 因子创建日期：20190729
    * 作者： 刘道一
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """
    
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.open_minute", "FactorData.Basic_factor.close_minute"\
    , "FactorData.Basic_factor.amt_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 1
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteOpen.index.strftime(fmt))
        compute_date = date_list[-1] 
        
        open_df = MinuteOpen.loc[compute_date]
        close_df = MinuteClose.loc[compute_date]
        tov_df = MinuteTurnover.loc[compute_date]
        T = open_df.shape[0]
        
        CLOSE = np.array(close_df.iloc[-1])
        CLOSE = CLOSE.reshape([1, CLOSE.shape[0]])
        
        data = (CLOSE / open_df).values - 1
        arr = data > 0
        return_df = pd.DataFrame(data,index=open_df.index,columns=open_df.columns)
        return_df_big = pd.DataFrame(arr,index=open_df.index,columns=open_df.columns)
        
        total_profitable_tov = tov_df[return_df_big].sum(axis = 0)
        
        result = (return_df * tov_df)[return_df_big].sum(axis = 0) / total_profitable_tov
        
        # centering on cross-section
        result = np.abs(result - result.median())
        
        return -result