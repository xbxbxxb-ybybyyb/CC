# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""
*因子名 : AmtRatioEntropy
*因子功能描述 : 20日成交额占比的信息熵
*因子逻辑：熵值越高，表明成交量分布越离散，后市看涨
*作者 : 沈天琦
*因子创建日期 : 2020.03.23
"""
class AmtRatioEntropy(BaseFactor):
	factor_type = 'DAY'
	depend_data = ["FactorData.Basic_factor.amt"]
	
	lag = 20
	
	# 返回： pd.Series

	def calc_single(self, database):

		df_amt = database.depend_data["FactorData.Basic_factor.amt"]

		df_amt_ratio = pd.DataFrame(df_amt.values / df_amt.sum(axis=0).values,index=df_amt.index, columns=df_amt.columns)
		

		result = -(df_amt_ratio * np.log(df_amt_ratio)).sum(axis=0)

		return result
