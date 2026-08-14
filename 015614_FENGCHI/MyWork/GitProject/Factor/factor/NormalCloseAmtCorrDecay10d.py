# -*- coding: utf-8 -*-
"""
* 因子名：NormalCloseAmtCorrDecay10d
* 因子功能描述： 找到每日正常时间（amt在两倍标准差以内的时候）的量价相关性。负向。越高越有炒作情绪。
* 因子参数：  MinuteTurnover,MinuteClose
* 作者：刘正
* 因子创建日期： 20190701
* 函数修改日期： 尚未修改
* 修改人： 尚未修改
* 修改原因：尚未修改
"""
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class NormalCloseAmtCorrDecay10d(BaseFactor):
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 0
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 20

    def calc_single(self, database):

        minute_data_transform(database.depend_data, operation=["drop","merge"])
        MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
        MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']

        score= (MinuteTurnover-MinuteTurnover.mean())/MinuteTurnover.std()

        score_less_2 = pd.DataFrame(score.values < 2, index=score.index, columns=score.columns)

        return Util.array_coef(MinuteClose[score_less_2], MinuteTurnover[score_less_2])

    def reform(self, temp_result):
        return -temp_result.rolling(10,min_periods=1).apply(self.decay)

    # def definition(self, MinuteTurnover,MinuteClose):
    #     factor = self.minute_help(self.minute, 'NormalCloseAmtCorrDecay10d_13hHelp', MinuteTurnover,MinuteClose)
    #     return  -factor.rolling(10,min_periods=1).apply(self.decay)
    
    # def minute(self, MinuteTurnover,MinuteClose ):
    #     date_list = sorted(np.unique(MinuteClose.index.strftime('%Y-%m-%d')))
    #     score= (MinuteTurnover-MinuteTurnover.mean())/MinuteTurnover.std()
    #     return MinuteClose[score<2].corrwith(MinuteTurnover[score<2])
    
    def decay(self, x):
        period = len(x)
        decay_days =10.0
        w = np.array([pow(pow(1/2,1/decay_days), period - 1 - i) for i in range(period)])
        w= w/sum(w)
        return np.sum(w*x)