"""
    * 因子名：MinPreTopVolRat
    * 因子功能描述：昨日尾盘top30%与bottom收益率成交量占比总成交量
    * 因子参数：  MinuteClose
    * 作者：肖倩
    * 因子创建日期： 20190520
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class MinPreTopVolRate(BaseFactor):
    
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute','FactorData.Basic_factor.volume_minute']    
    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 5

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        fmt = '%Y-%m-%d'
        date_list = np.unique(MinuteClose.index.strftime(fmt))

        compute_date = date_list[-1]
        pre_date = date_list[-2]
        close_df = MinuteClose.loc[pre_date]
        volume_df = MinuteVolume.loc[pre_date]
        return_df = close_df.pct_change(1).iloc[-60:]
        vol = volume_df.iloc[-60:]
        ret_rank = return_df.rank(axis=0,pct=True)

        ret_rank_gt_0_3 = pd.DataFrame(ret_rank.values>0.3, index=ret_rank.index, columns=ret_rank.columns)
        ret_rank_ls_0_3 = pd.DataFrame(ret_rank.values<0.3, index=ret_rank.index, columns=ret_rank.columns)

        result= (vol[ret_rank_gt_0_3].sum()-vol[ret_rank_ls_0_3].sum())/vol.sum()
        
        return result

    def reform(self, temp_result):

        return -temp_result.rolling(window=5,min_periods=1).apply(lambda x:self.ewm(x))
    # def definition(self, MinuteClose,MinuteVolume):

    #     result = self.minute_help(self.minute, 'MinPreTopVolRatHelp', MinuteClose,MinuteVolume)
    #     result = result.rolling(window=5,min_periods=1).apply(lambda x:self.ewm(x))
    #     return -1*result

    # def minute(self, MinuteClose,MinuteVolume):

    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     result = pd.DataFrame(np.nan, index=[pd.Timestamp(date) for date in date_list], columns=MinuteClose.columns)
    #     compute_date = date_list[-1]
    #     pre_date = date_list[-2]
    #     close_df = MinuteClose.loc[pre_date]
    #     volume_df = MinuteVolume.loc[pre_date]
    #     return_df = close_df.pct_change(1).iloc[-60:]
    #     vol = volume_df.iloc[-60:]
    #     ret_rank = return_df.rank(axis=0,pct=True)
    #     result= (vol[ret_rank>0.3].sum()-vol[ret_rank<0.3].sum())/vol.sum()
        
    #     return result
        
    def ewm(self,x):
        window=len(x)
        seq = [(1-(2.0/(window+1))) ** (window-i) for i in range(1, window + 1)]
        weight = np.array(seq)
        weight_sum = np.sum(weight)
        return np.nansum(x * weight) / weight_sum
