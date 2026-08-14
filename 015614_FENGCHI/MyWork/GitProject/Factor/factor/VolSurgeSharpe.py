# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""
*因子名 : VolSurgeSharpe
*因子功能描述 : 成交量急速扩大时收益率的夏普取负
*因子逻辑：极度增量推高股价后，后市看跌
*作者 : 沈天琦
*因子创建日期 : 2020.03.10
"""
class VolSurgeSharpe(BaseFactor):
	factor_type = 'DAY'
	depend_data = ["FactorData.Basic_factor.volume", "FactorData.Basic_factor.close", "FactorData.Basic_factor.adjfactor"]

	lag = 60
	# 返回： pd.Series

	def calc_single(self, database):

		df_close = database.depend_data["FactorData.Basic_factor.close"]
		df_volume = database.depend_data["FactorData.Basic_factor.volume"]

		df_adjfactor = database.depend_data["FactorData.Basic_factor.adjfactor"]

		df_close_adj = df_close * df_adjfactor
		df_volume_adj = df_volume / df_adjfactor

		df_rtn = (df_close_adj - df_close_adj.shift(1)) / df_close_adj.shift(1)
		vol_growth_minute = (df_volume_adj - df_volume_adj.shift(1)) / df_volume_adj.shift(1)
		
		is_vol_up = pd.DataFrame((vol_growth_minute.values > 0) & (vol_growth_minute.values > vol_growth_minute.rolling(window=10,min_periods=1).mean().values), index=vol_growth_minute.index, columns=vol_growth_minute.columns) 
	
		rtn_vol_surge = df_rtn[is_vol_up]

		result = -rtn_vol_surge.mean(axis=0) / rtn_vol_surge.std(axis=0)

		return result
