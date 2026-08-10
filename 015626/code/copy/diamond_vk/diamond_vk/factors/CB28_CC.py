from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB28_CC(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close','high']
		super(CB28_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		close = df['close'][-240:].between_time(data_morning_begin, trade_stop_time)
		close = close.groupby(close.index.date).last()
		close.index = pd.to_datetime(close.index)
		high = df['high'][-240:].between_time(data_morning_begin, trade_stop_time)
		high = high.groupby(high.index.date).max()
		high.index = pd.to_datetime(high.index)

		factor = high/close

		factor.index = pd.to_datetime(factor.index)
		factor = factor.replace([-np.inf, np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor