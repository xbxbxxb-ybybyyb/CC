from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class CB27_CC(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close']
		super(CB27_CC, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		hclose = df['close'].between_time(datetime.time(14, 0), trade_stop_time)
		hclose = hclose.groupby(hclose.index.date)
		factor = ts_mean(hclose.last()/hclose.first()-1, 15) * -1

		factor.index = pd.to_datetime(factor.index)
		factor = factor.replace([-np.inf, np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor