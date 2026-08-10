from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class kzz_crssuper(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close']
		super(kzz_crssuper, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		c = df['close'][-3000:].pct_change(5)
		c = ts_std(c, 2400)
		f = c.between_time(data_morning_begin, trade_stop_time)
		tday = df['close'].index.date[-1]
		factor = f.loc[tday:].mean().to_frame()

		factor = factor.replace([np.inf, -np.inf], np.nan)

		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor