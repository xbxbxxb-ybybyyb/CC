from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform
import numpy as np
import pandas as pd
import time


class CorrPVLowLiquidity(BaseFactor):  # 派生一个因子类
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.open_minute','FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    minute_lag=0
    # fix_times = ["1300"]
    # reform_window = 5



    """
    * 因子名：CorrPVLowLiquidity_13h
    * 因子功能描述：计算T+0日流动性大于0.75百分位的量价相关性。
    * 因子参数： MinuteClose， MinuteVolume
    * 作者：姚逸凡
    * 因子创建日期： 2019.8.16
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
    """

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
        MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

        _open = MinuteOpen
        volume = MinuteVolume
        volume = volume.fillna(0.0)
        # ret = _open.pct_change(1)
        ret = _open.diff()/_open.shift()
        liquidity = ret / volume
        cond = pd.DataFrame((liquidity.values > liquidity.quantile(0.75).values), index=ret.index, columns=ret.columns) 
        open_new = _open[cond]
        volume_new = volume[cond]
        # corr = -open_new.corrwith(volume_new)
        corr = Util.array_coef(open_new, volume_new)
        return -corr
