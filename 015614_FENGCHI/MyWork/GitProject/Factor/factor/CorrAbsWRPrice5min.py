from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class CorrAbsWRPrice5min(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.high_minute', 'FactorData.Basic_factor.low_minute',
                    'FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1300"]
    # reform_window = 5


    '''
    * 因子名：AbnormalPriceDiff_13h
    * 描述：前日到今日异常交易后45分钟价格波动的绝对值的偏度负数，异常交易为价格的变化与波动率比值大于2
    * 逻辑：因子值越大表示低价格变动越大表示价格大幅变动之后变化越小，股票优势，建议持有
    * 因子参数：分钟数据的收高低、量、换手
    * 作者：孔剑阳
    * 日期：2019.9.23
    * 函数修改日期：尚未修改
    * 修改人：尚未修改
    * 修改原因：尚未修改
    '''
    
    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

        close_min = MinuteClose.rolling(window=5,min_periods=4).mean()
        high_min = MinuteHigh.rolling(window=5,min_periods=4).max()
        low_min = MinuteLow.rolling(window=5,min_periods=4).min()
        # wr = (2*close_min.values-high_min-low_min).abs()/(high_min-low_min)
        wr = np.abs(2*close_min.values-high_min.values-low_min.values)/(high_min.values-low_min.values)
        wr = pd.DataFrame(wr, index=close_min.index, columns=close_min.columns)
        # CorrAbsWRPrice = wr.rank(axis=0).corrwith(close_min.rank(axis=0),axis=0)
        CorrAbsWRPrice = Util.array_coef(wr.rank(axis=0), close_min.rank(axis=0))
        return CorrAbsWRPrice