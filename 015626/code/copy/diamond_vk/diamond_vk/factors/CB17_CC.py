from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB17_CC(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close']
		super(CB17_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		temp = df['close'][-500:].between_time(data_morning_begin, trade_stop_time)
      
		temp = temp.groupby(temp.index.date)

		factor = abs(temp.last()/temp.first().shift(1)-1)
		factor.index = pd.to_datetime(factor.index)
		factor = factor.replace([-np.inf, np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor