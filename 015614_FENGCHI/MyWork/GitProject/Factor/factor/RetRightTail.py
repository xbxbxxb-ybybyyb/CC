# -*- coding: utf-8 -*-
'''
* 因子名称：RetRightTail
* 描述：T-1日Vwap分钟收益率超过80%分位数的部分的成交量加权平均数，取20日sharpe
* 因子逻辑：将Vwap分钟收益率超过80%分位数的部分视为主动买单，如果过去20天内有明显且持续的主动买单，预示股票有上涨潜力
* 因子参数：分钟数据的成交额、成交量
* 作者：何丰敬
* 日期：2019.8.24
* 函数修改日期:尚未修改
* 修改人：尚未修改
* 修改原因：尚未修改
'''
import numpy as np
import pandas as pd

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

class RetRightTail(BaseFactor):
    
    factor_type = 'FIX'             # 声明因子类型为FIX
    depend_data = ['FactorData.Basic_factor.amt_minute', 'FactorData.Basic_factor.volume_minute']    # 声明因子计算需要依赖的数据字段，必需设置
    # 计算每个时点的因子所需要前移的数据窗口大小
    # 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
    lag = 0
    # 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
    minute_lag = 1
    # 定义单次播放时，因子值的计算方法
    # 返回： pd.Series
    reform_window = 20

    def calc_single(self, database):
        
        minute_data_transform(database.depend_data, operation = ["drop", "merge"])
        turnover_minute = database.depend_data['FactorData.Basic_factor.amt_minute']
        volume_minute = database.depend_data['FactorData.Basic_factor.volume_minute']

        r = (turnover_minute / volume_minute).iloc[:240].pct_change()  # T-1日Vwap分钟收益率
        r_q = r.quantile(0.8)  # 取80%分位数
        bool_statement = pd.DataFrame(r.values > r_q.values, index=r.index, columns=r.columns)
        vol = volume_minute.iloc[:240].where(bool_statement)
        r = r.where(bool_statement)
        r_e = (r * vol).sum() / vol.sum()  # 超过80%分位数部分的成交量加权平均
        return r_e - r_q

    def reform(self, temp_result):
        return temp_result.rolling(self.reform_window).mean() / temp_result.rolling(self.reform_window).std()


    # def definition(self, MinuteTurnover, MinuteVolume):
    #     factor = self.minute_help(self.minute, 'MinuteValidRetHelp', MinuteTurnover, MinuteVolume).rolling(20)
    #     return factor.mean() / factor.std()  # 取20日sharpe

    
    # def minute(self, MinuteTurnover, MinuteVolume):
    #     r = (MinuteTurnover / MinuteVolume).iloc[:240].pct_change()  # T-1日Vwap分钟收益率
    #     r_q = r.quantile(0.8)  # 取80%分位数
    #     vol = MinuteVolume.iloc[:240].where(r > r_q)
    #     r = r.where(r > r_q)
    #     r_e = (r * vol).sum() / vol.sum()  # 超过80%分位数部分的成交量加权平均
    #     return r_e - r_q
