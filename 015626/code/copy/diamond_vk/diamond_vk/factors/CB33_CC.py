from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB33_CC(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close']
		super(CB33_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		# hclose = df['close'].pct_change(30).between_time(datetime.time(10,0), trade_stop_time)

		# temp = hclose.groupby(hclose.index.date).std()

		# f = ts_mean(temp, 10).rank(axis = 1, pct = True)*2-1

		hclose = df['close'].pct_change(30).between_time('1000', '1449')

		temp = hclose.groupby(hclose.index.date).std()

		f = temp.rolling(10, min_periods = 2).mean().rank(axis = 1, pct = True)*2-1
		factor = abs(f)

		factor.index = pd.to_datetime(factor.index)
		factor = factor.replace([-np.inf, np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor