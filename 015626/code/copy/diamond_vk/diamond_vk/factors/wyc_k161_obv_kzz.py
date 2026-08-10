from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k161_obv_kzz(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['close','volume']
		super(wyc_k161_obv_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		close = df['close'].between_time(data_morning_begin, trade_stop_time)
		close = close.groupby(close.index.date).last()
		close.index = pd.to_datetime(close.index)
		volume = df['volume'].between_time(data_morning_begin, trade_stop_time)
		volume = volume.groupby(volume.index.date).sum()
		volume.index = pd.to_datetime(volume.index)

		con1 = close > ts_delay(close, 1)
		OBV = pd.DataFrame(columns=close.columns, index = close.index)
		OBV[con1] = volume
		con2 = close < ts_delay(close, 1)
		OBV[~con1 & con2] = -1 * volume
		OBV[~con1 & ~con2] = 0
		factor = ts_sum(OBV, 20)

		factor = factor.replace([np.inf, -np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor