# -*- coding: utf-8 -*-


'''
相对强弱指标，分钟高低价的beta
负向。光大的rsrs指标短期内有反转现象

'''

import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


class Rsrs(BaseFactor):

	factor_type = 'FIX'             # 声明因子类型为FIX
	depend_data = ['FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute']    # 声明因子计算需要依赖的数据字段，必需设置
	# 计算每个时点的因子所需要前移的数据窗口大小
	# 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
	lag = 0
	# 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
	minute_lag = 1
	# 定义单次播放时，因子值的计算方法
	# 返回： pd.Series

	def calc_single(self, database):
		minute_data_transform(database.depend_data, operation=["drop","merge"])
		MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
		MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

		rs = MinuteHigh.std(axis=0)/MinuteLow.std(axis=0)*(Util.array_coef(MinuteHigh,MinuteLow))

		return -rs

	# def definition(self,  MinuteHigh, MinuteLow ):
	#     factor = self.minute_help(self.minute, 'Rsrs_13h' +'Help', MinuteHigh, MinuteLow)
	#     return -factor

	# def minute(self,MinuteHigh,MinuteLow): 
	#     date_list = sorted(np.unique(MinuteHigh.index.strftime('%Y-%m-%d')))
	#     date = date_list[-1]
	#     pre_date = date_list[-2]
	#     rs = MinuteHigh.std(axis=0)/MinuteLow.std(axis=0)*(MinuteHigh.corrwith(MinuteLow))

	#     return rs

	