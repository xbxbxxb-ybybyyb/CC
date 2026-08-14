# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

'''
高低价差-开收价差为溢出，单位成交额的溢出 5日均值
正向。蜡烛图里两头的线为overflow，越高说明潜力越大

'''
class OverflowPerAmtMean5d(BaseFactor):
	factor_type = 'FIX'             # 声明因子类型为FIX
	depend_data = ['FactorData.Basic_factor.high_minute','FactorData.Basic_factor.low_minute','FactorData.Basic_factor.amt_minute','FactorData.Basic_factor.open_minute','FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
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

		MinuteTurnover = database.depend_data['FactorData.Basic_factor.amt_minute']
		MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
		MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
		MinuteHigh = database.depend_data['FactorData.Basic_factor.high_minute']
		MinuteLow = database.depend_data['FactorData.Basic_factor.low_minute']

		overflow= (MinuteHigh-MinuteLow)-abs(MinuteOpen-MinuteClose)
		return (overflow/MinuteTurnover).sum()

	def reform(self, temp_result):
		return temp_result.rolling(self.reform_window,min_periods=1).mean()

	# def definition(self, MinuteTurnover,MinuteOpen,MinuteClose,MinuteHigh,MinuteLow):
	#     factor = self.minute_help(self.minute, 'OverflowPerAmtMean5d_13hHelp', MinuteTurnover,MinuteOpen,MinuteClose,MinuteHigh,MinuteLow)
	#     return factor.rolling(5,min_periods=1).mean()

	# def minute(self, MinuteTurnover,MinuteOpen,MinuteClose,MinuteHigh,MinuteLow):
	#     date_list = sorted(np.unique(MinuteTurnover.index.strftime('%Y-%m-%d')))
	#     date = date_list[-1]
	#     pre_date = date_list[-2]
	#     overflow= (MinuteHigh-MinuteLow)-abs(MinuteOpen-MinuteClose)
	#     return (overflow/MinuteTurnover).sum()