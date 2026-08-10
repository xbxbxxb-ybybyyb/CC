from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k31_arc_kzz(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close','amount']
		super(wyc_k31_arc_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		#收益率与成交额的相关性
		c = df['close'].between_time(data_morning_begin, trade_stop_time)
		a = df['amount'].between_time(data_morning_begin, trade_stop_time)
		g = c.groupby(c.index.date)
		r = g.last() / g.first() - 1
		r = r.replace([np.inf, -np.inf], np.nan)

		a = a.groupby(a.index.date).sum()
		N = 10
		factor = a[-1*N:].corrwith(r[-1*N:]).to_frame()
		factor = factor.replace([np.inf, -np.inf], np.nan)

		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor