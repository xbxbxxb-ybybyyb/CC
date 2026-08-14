import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
    * 因子名：MinUpDownVolRet
    * 因子功能描述：计算上行市成交额与下行市场成交额之比
    * 因子参数：  MinuteClose, MinuteVolume
    * 作者：肖倩
    * 因子创建日期： 2019.6.23
"""

class MinUpDownVolRet(BaseFactor):

    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute', 'FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    
    def calc_single(self, database):
        
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])

        close_df = database.depend_data['FactorData.Basic_factor.close_minute']
        volume_df = database.depend_data['FactorData.Basic_factor.volume_minute']
        ret = close_df.pct_change(periods=1)
        
        ret_up = ret[pd.DataFrame(ret.values > 0, index=ret.index, columns=ret.columns)]
        ret_down = ret[pd.DataFrame(ret.values < 0, index=ret.index, columns=ret.columns)]

        vol_ratio = pd.DataFrame(volume_df.values / volume_df.sum().values, index=volume_df.index, columns=volume_df.columns)

        # return -(ret[ret_up] * volume_df/ volume_df.sum()).sum()-(ret[ret_down] * volume_df/ volume_df.sum()).sum()

        return (ret_down * vol_ratio).sum() - (ret_up * vol_ratio).sum()
        

    # def definition(self, MinuteClose, MinuteVolume):

    #     result = self.minute_help(self.minute, 'MinUpDownVolRetHelp', MinuteClose, MinuteVolume)
    #     return -1*result
    # def minute(self, MinuteClose, MinuteVolume):

    #     fmt = '%Y-%m-%d'
    #     date_list = np.unique(MinuteClose.index.strftime(fmt))
    #     compute_date = date_list[-1]
    #     close_df = MinuteClose.loc[compute_date]
    #     volume_df = MinuteVolume.loc[compute_date]
    #     ret = close_df.pct_change(periods=1)
    #     return (ret[ret > 0] * volume_df/ volume_df.sum()).sum()-(ret[ret < 0] * volume_df/ volume_df.sum()).sum()


