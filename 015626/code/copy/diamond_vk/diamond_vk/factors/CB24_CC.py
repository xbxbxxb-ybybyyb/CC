from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB24_CC(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['amount']
		super(CB24_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		f1 = rolling_norm(df['amount'], 1200).between_time(data_morning_begin, trade_stop_time)
		f = f1.groupby(f1.index.date).sum()

		factor = abs(ts_reg_beta(f, 30))

		factor.index = pd.to_datetime(factor.index)
		factor = factor.replace([-np.inf, np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor