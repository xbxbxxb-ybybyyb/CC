"""
    * 因子名：MinPriceAutoCorr_13h
    * 因子功能描述：计算分钟最高价与最低价价格比率与收盘价之间的秩相关性，是一个反转因子，该值越大则越容易往下跌
    * 因子参数：  MinuteClose,MinuteHigh, MinuteLow
    * 作者： 肖倩
    * 因子创建日期： 2019.7.8
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
from xfactor.FixUtil import min_forward_adj

class MinPriceAutoCorr(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute','FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute']    
    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    # reform_window = 5

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
        MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))
        compute_date = date_list[-1]
        close_df = MinuteClose.loc[compute_date]
        high_df = MinuteHigh.loc[compute_date]
        low_df = MinuteLow.loc[compute_date]
        hl_df = (high_df/low_df)

        return -Util.array_coef(hl_df.rank(axis=1), close_df.rank(axis=1))

    # def definition(self, MinuteClose,MinuteHigh, MinuteLow):

    #     result = self.minute_help(self.minute, 'MinPriceAutoCorrHelp', MinuteClose,MinuteHigh, MinuteLow)
        
    #     return -1*result

    # def minute(self, MinuteClose,MinuteHigh, MinuteLow):
    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     compute_date = date_list[-1]
    #     close_df = MinuteClose.loc[compute_date]
    #     high_df = MinuteHigh.loc[compute_date]
    #     low_df = MinuteLow.loc[compute_date]
    #     hl_df = (high_df/low_df)
    #     result = hl_df.rank(axis=1).corrwith(close_df.rank(axis=1),axis=0)
    #     return result