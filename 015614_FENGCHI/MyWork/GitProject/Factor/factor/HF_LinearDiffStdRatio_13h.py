from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
import numpy as np
import pandas as pd
from xfactor.FixUtil import minute_data_transform


class HF_LinearDiffStdRatio_13h(BaseFactor):
    """
    * 因子名：HF_LinearDiffStdRatio_13h
    * 因子功能描述：T日开盘到当前时刻线性趋势线分别与low和high之差的波动率之比
    * 因子参数：MinuteHigh,MinuteLow,MinuteClose
    * 作者：游加平
    * 因子创建日期： 2019.11.01
    """
    factor_type = "FIX"
    # 依赖的平台原始数据，包括FactorData和MarketData接口中的数据。 默认为空，必须设置
    depend_data = ["FactorData.Basic_factor.high_minute", "FactorData.Basic_factor.close_minute"\
    , "FactorData.Basic_factor.low_minute"]
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 例如，为日频因子，lag=3表示计算某一日的因子值需要依赖前三个交易日和当日的数据，默认为0，可不设置
    lag = 0
    reform_window = 0

    def calc_single(self, database):
        minute_data_transform(database.depend_data, operation = ["merge", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(MinuteClose.index.strftime(fmt)))
        compute_date = date_list[-1]
        close = MinuteClose.loc[compute_date]
        high = MinuteHigh.loc[compute_date]
        low = MinuteLow.loc[compute_date]
        
        coef = np.linspace(0,1,close.shape[0])
        coef = pd.DataFrame(np.array( ([coef] * close.shape[1]) ).T,index=close.index,columns=close.columns)
        arr = coef.values*(close.iloc[-1]-close.iloc[0]).values+close.iloc[0].values
        linear = pd.DataFrame(arr,index=coef.index,columns=coef.columns)
        #linear = coef.mul(close.iloc[-1]-close.iloc[0],axis=1).add(close.iloc[0],axis=1)
        ratio = (linear - low).std() / (linear - high).std()        
        return ratio
