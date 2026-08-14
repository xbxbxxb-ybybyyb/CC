# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np

from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util

from xfactor.FixUtil import minute_data_transform
"""
*因子名 : ExtremeTurnStd
*因子功能描述 : 极端高收益的分钟换手率的五日波动率再取负
*因子逻辑：寻找每日收益被极度推高的分钟成交量之和计算与自由流通股本的换手率取负，极端换手率越低，后市越看涨，这种情况越稳定，后市看涨愈加强烈。
*作者 : 沈天琦
*因子创建日期 : 2020.03.11
"""
class ExtremeTurnStd(BaseFactor):
	factor_type = 'DAY'
	depend_data = ["FactorData.Basic_factor.free_float_shares", "FactorData.Basic_factor.close_minute","FactorData.Basic_factor.volume_minute"]
	# 计算每个时点的因子所需要前移的数据窗口大小
	
	lag = 0
	minute_lag = 0
	
	reform_window = 5
	# 返回： pd.Series

	def calc_single(self, database):

		data_minute = {"FactorData.Basic_factor.close_minute":database.depend_data['FactorData.Basic_factor.close_minute']
		                ,"FactorData.Basic_factor.volume_minute":database.depend_data['FactorData.Basic_factor.volume_minute']}
		minute_data_transform(data_minute,operation=['drop','merge'])

		df_free_shares = database.depend_data["FactorData.Basic_factor.free_float_shares"]

		close_minute = data_minute["FactorData.Basic_factor.close_minute"]
		volume_minute = data_minute["FactorData.Basic_factor.volume_minute"]

		rtn_minute = (close_minute - close_minute.shift(1)) / close_minute.shift(1)
		
		is_rtn_extreme = pd.DataFrame((rtn_minute.values > rtn_minute.mean(axis=0).values + 4*rtn_minute.std(axis=0).values),index=rtn_minute.index,columns=rtn_minute.columns)

		df_extreme_vol = volume_minute[is_rtn_extreme]

		df_extreme_vol.fillna(value=0,inplace=True)

		result =  -df_extreme_vol.sum(axis=0) / df_free_shares.iloc[-1]
		
		return result

	def reform(self,temp_result):

		return -temp_result.rolling(window=self.reform_window,min_periods=1).std()