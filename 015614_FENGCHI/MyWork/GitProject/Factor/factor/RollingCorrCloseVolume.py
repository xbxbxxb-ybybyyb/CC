# -*- coding: utf-8 -*-
"""
	* 因子名：RollingCorrCloseVolume
	* 因子功能描述：计算T-1日开盘到目前时刻的价格与成交量的5日相关性。
	* 因子参数：  MinuteOpen, MinuteVolume
	* 作者：姚逸凡
	* 因子创建日期： 2019.7.26
	* 函数修改日期： 尚未修改
	* 修改人： 尚未修改
	* 修改原因：尚未修改
"""
import numpy as np
import pandas as pd
from xfactor.BaseFactor import BaseFactor
import xfactor.Util as Util
from xfactor.FixUtil import minute_data_transform


class RollingCorrCloseVolume(BaseFactor):

	factor_type = 'FIX'             # 声明因子类型为FIX
	depend_data = ['FactorData.Basic_factor.volume_minute','FactorData.Basic_factor.open_minute']    # 声明因子计算需要依赖的数据字段，必需设置
	# 计算每个时点的因子所需要前移的数据窗口大小
	# 当lag = n时，每次播放时将提供 242 * (n+1) 根分钟线数据，默认lag=0，可不设置
	lag = 0
	# 定义分钟线minute_lag天数，该参数用于分离分钟前窗口的长度和日频数据的长度，当minute_lag = n时，每次calc_single提供的分钟数据有(n+1)*240行。若不设置minute_lag，则框架默认minute_lag = lag
	minute_lag = 6
	# 定义单次播放时，因子值的计算方法
	# 返回： pd.Series

	def calc_single(self, database):

		minute_data_transform(database.depend_data, operation=["drop","merge"])
		
		MinuteOpen = database.depend_data['FactorData.Basic_factor.open_minute']
		MinuteVolume = database.depend_data['FactorData.Basic_factor.volume_minute']

		fmt = '%Y-%m-%d'
		date_list = sorted(np.unique(MinuteOpen.index.strftime(fmt)))

		ret_df = pd.DataFrame()
		volume_df = pd.DataFrame()

		for i in range(len(date_list)-1):
			pre_date = date_list[i]
			compute_date = date_list[i+1]

			close_yesterday = MinuteOpen.loc[pre_date]
			netv = close_yesterday.iloc[-1]

			ret_df = ret_df.append(netv)
			volume_df = volume_df.append(MinuteVolume.loc[pre_date].sum() + MinuteVolume.loc[compute_date].sum(),ignore_index=True)


		return -Util.rolling_corr(ret_df,volume_df,5).iloc[-1]


	# def definition(self, MinuteOpen, MinuteVolume):
	#     result = self.minute_help(self.minute, 'MinuteValidRetHelp',MinuteOpen, MinuteVolume)
	#     vol = result['volume']
	#     ret = result['ret']
	#     corr = -ret.rolling(5, min_periods=3).corr(vol)
	#     return corr

	# def minute(self, MinuteOpen, MinuteVolume):

	#     fmt = '%Y-%m-%d'
	#     date_list = sorted(np.unique(MinuteOpen.index.strftime(fmt)))
	#     compute_date = date_list[-1]
	#     pre_date = date_list[-2]
	#     close_yesterday = MinuteOpen.loc[pre_date]
	#     netv = close_yesterday.iloc[-1]
	#     result = {}
	#     result['ret'] = netv
	#     result['volume'] =  MinuteVolume.loc[pre_date].sum() + MinuteVolume.loc[compute_date].sum()

	#     return result
