# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""
*因子名 : RtnVolGrowthRankDiff
*因子功能描述 : 10日收盘价收益率及成交量增长率的排名差根据涨跌区分再取均值
*因子逻辑：缩量上涨、放量下跌后看涨，反之看跌
*作者 : 沈天琦
*因子创建日期 : 2020.03.26
"""
class RtnVolGrowthRankDiff(BaseFactor):
	factor_type = 'DAY'
	depend_data = ["FactorData.Basic_factor.close","FactorData.Basic_factor.volume","FactorData.Basic_factor.adjfactor"]
	
	lag = 10
	
	# 返回： pd.Series

	def calc_single(self, database):

		df_close = database.depend_data["FactorData.Basic_factor.close"] * database.depend_data["FactorData.Basic_factor.adjfactor"]
		df_volume = database.depend_data["FactorData.Basic_factor.volume"] / database.depend_data["FactorData.Basic_factor.adjfactor"]
		

		df_rtn = (df_close - df_close.shift(1)) / df_close.shift(1)
		df_vol_growth = (df_volume - df_volume.shift(1)) / df_volume.shift(1)

		df_rtn_sign = np.sign(df_rtn)
		
		result = ((df_rtn.rank() - df_vol_growth.rank()) * df_rtn_sign).mean()
		
		return result
