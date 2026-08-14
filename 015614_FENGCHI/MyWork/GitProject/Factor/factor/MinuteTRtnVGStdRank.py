from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time




class MinuteTRtnVGStdRank(BaseFactor):  # 派生一个因子类
    """

    * 因子名 : MinuteSignedAvgDistanceDiffMean
    * 因子功能描述 : 捕将分钟数据划分为5min线，分别求当前close在vwap的上方、下方的总面积，两者绝对值比值乘以尾盘30分钟价格方向。5日平均做因子值。
    * 因子参数：MinuteTurnover, MinuteClose，MinuteVolume
    * 作者：刘道一
    * 因子创建日期： 2019.5.18
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改

    """ 
    factor_type = 'DAY'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.volume_minute', 
                    'FactorData.Basic_factor.close_minute']  
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1500"]
    # reform_window = 5
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    """

    *因子名 : MinuteTRtnVGStdRank
    *因子功能描述 : 在极端收益率较低情况下，成交量增长率的波动率排序
    *因子参数 : MinuteClose-分钟末端成交价格, MinuteVolume-分钟成交量
    *作者 : 沈天琦(shentq)
    *因子创建日期 : 2019.05.27
    *函数修改日期 : 尚未修改
    *修改人 ：尚未修改
    *修改原因 :  尚未修改


    """


    def calc_single(self, database):


        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        minute_close = database.depend_data['FactorData.Basic_factor.close_minute']
        minute_volume = database.depend_data['FactorData.Basic_factor.volume_minute']

        # minute_close = MinuteClose.loc[date]
        # minute_volume = MinuteVolume.loc[date]

        # minute_close_return = minute_close.pct_change(1)
        # minute_volume_growth_rate = minute_volume.pct_change(1)
        minute_close_return = (minute_close-minute_close.shift())/minute_close.shift()
        minute_volume_growth_rate = (minute_volume-minute_volume.shift())/minute_volume.shift()

        minute_volume_growth_rate[~np.isfinite(minute_volume_growth_rate)] = np.nan

        rg = minute_close_return.mean().values-2*minute_close_return.std().values
        rg = np.tile(rg,(minute_close.shape[0],1))
        rg = pd.DataFrame(rg, index = minute_close.index, columns = minute_close.columns)
        # print(minute_volume_growth_rate)
        # print(minute_volume_growth_rate[minute_close_return < rg][-60:])

        minute_vol_rate_low = minute_volume_growth_rate[minute_close_return < rg][-60:]
        
        df_factor = minute_vol_rate_low.std().rank()
        
        return df_factor