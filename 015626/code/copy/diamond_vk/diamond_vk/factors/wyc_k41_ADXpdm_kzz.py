from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k41_ADXpdm_kzz(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['high','low','close']
		super(wyc_k41_ADXpdm_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		close = df['close'].between_time(data_morning_begin, trade_stop_time)
		close = close.groupby(close.index.date).last()
		close.index = pd.to_datetime(close.index)
		high = df['high'].between_time(data_morning_begin, trade_stop_time)
		high = high.groupby(high.index.date).max()
		high.index = pd.to_datetime(high.index)
		low = df['low'].between_time(data_morning_begin, trade_stop_time)
		low = low.groupby(low.index.date).min()
		low.index = pd.to_datetime(low.index)

		N = 40
		max_high = MAX(high - ts_delay(high,1), 0)
		max_low = MAX(ts_delay(low, 1) - low, 0)
		xpdm = pd.DataFrame(0,columns = max_high.columns, index = max_high.index)
		xpdm[max_high > max_low] = high - ts_delay(high, 1)
		pdm = ts_sum(xpdm, N)
		tr = MAX(abs(high - low), abs(high - close))
		tr = MAX(tr, abs(low - close))
		tr = ts_sum(tr, N)
		factor = (pdm) / tr
		factor = factor.replace([np.inf, -np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor