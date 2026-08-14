# -*- coding: utf-8 -*-
import numpy as np
import pandas as pd

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform

"""
	* 因子名：PriceDeviationBias10d
	* 因子功能描述：
	* 因子参数：  MinuteClose,MinuteHigh, MinuteLow
	* 作者： 
	* 因子创建日期： 
"""

class PriceDeviationBias10d(BaseFactor):

	factor_type = 'FIX'             # 声明因子类型为FIX
	depend_data = ['FactorData.Basic_factor.open_minute','FactorData.Basic_factor.close_minute']    # 声明因子计算需要依赖的数据字段，必需设置
	# 计算每个时点的因子所需要前移的数据窗口大小
	# 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
	lag = 0
	# 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
	minute_lag = 0
	# 定义单次播放时，因子值的计算方法
	# 返回： pd.Series
	reform_window = 10

	def calc_single(self, database):
		minute_data_transform(database.depend_data, operation = ["drop", "merge"])

		MinuteClose = database.depend_data['FactorData.Basic_factor.close_minute']
		MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']

		close_diff_values = (MinuteClose.values-MinuteClose.mean().values)
		open_values = MinuteOpen.iloc[0].values

		return pd.DataFrame((close_diff_values/open_values), index=MinuteClose.index, columns=MinuteClose.columns).max()

	def reform(self, temp_result):

		return -(temp_result-temp_result.rolling(self.reform_window).mean())/temp_result.rolling(self.reform_window).std()

  #   def definition(self, MinuteClose,MinuteOpen,):
  #       factor = self.minute_help(self.minute, 'internal',MinuteClose,MinuteOpen)
  #       return -(factor-factor.rolling(10).mean())/factor.rolling(10).std()

  #   def minute(self,MinuteClose, MinuteOpen):
  #       fmt = '%Y-%m-%d'
  #       date_list = sorted(np.unique(MinuteOpen.index.strftime(fmt)))
		# return ((MinuteClose-MinuteClose.mean())/MinuteOpen.iloc[0,:]).max()


		