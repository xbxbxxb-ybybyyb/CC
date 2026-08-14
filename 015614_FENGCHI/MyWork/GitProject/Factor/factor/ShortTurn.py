# -*- coding: utf-8 -*-
"""
    * 因子名：ShortTurn
    * 因子功能描述：计算分钟收益率为负的换手率，负换手率越大则预测跌
    * 因子参数：  MinuteClose, MinuteTurnover, mkt_cap_ard
    * 作者：姚逸凡
    * 因子创建日期： 2019.6.24
    * 函数修改日期： 尚未修改
    * 修改人： 尚未修改
    * 修改原因：尚未修改
"""

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class ShortTurn(BaseFactor):
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.close_minute','FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.mkt_cap_ard']    
    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 2
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 2
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    # reform_window = 5

    def calc_single(self, database):
        data_minute = {'FactorData.Basic_factor.close_minute':database.depend_data['FactorData.Basic_factor.close_minute'],'FactorData.Basic_factor.amt_minute':database.depend_data['FactorData.Basic_factor.amt_minute']}
        minute_data_transform(data_minute, operation = ["drop", "merge"])

        fmt = '%Y-%m-%d'
        date_list = sorted(np.unique(data_minute['FactorData.Basic_factor.amt_minute'].index.strftime(fmt)))
        compute_date = date_list[-1]
        pre_date = date_list[-2]

        last_mkt_cap_ard = database.depend_data['FactorData.Basic_factor.mkt_cap_ard'].iloc[-2]
        turnover = data_minute['FactorData.Basic_factor.amt_minute'].loc[compute_date]
        close = data_minute['FactorData.Basic_factor.close_minute'].loc[compute_date]

        ret = close.pct_change(1)
        indicator = -turnover[pd.DataFrame(ret.values < 0,index=ret.index, columns=ret.columns)].sum() / last_mkt_cap_ard

        return indicator
        
    # def definition(self, MinuteClose, MinuteTurnover, mkt_cap_ard):
    #     factor = self.minute_help(self.minute, 'MinuteValidRetHelp',  MinuteClose, MinuteTurnover, mkt_cap_ard)
    #     return factor

    # def minute(self, MinuteClose, MinuteTurnover, mkt_cap_ard):

    #     fmt = '%Y-%m-%d'
    #     date_list = sorted(np.unique(MinuteTurnover.index.strftime(fmt)))
    #     compute_date = date_list[-1]
    #     pre_date = date_list[-2]
    #     turnover = MinuteTurnover.loc[compute_date]
    #     close = MinuteClose.loc[compute_date]
    #     ret = close.pct_change(1)
    #     indicator = -turnover[ret < 0].sum() / mkt_cap_ard.loc[pre_date]

    #     return indicator

