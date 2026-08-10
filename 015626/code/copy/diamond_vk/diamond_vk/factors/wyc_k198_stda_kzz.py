from diamond_vk.factor_generator import FactorGenerator
from diamond_vk.naming_config import *
from diamond_vk.utility import *
import datetime
import numpy as np
import bottleneck as bk
import pandas as pd

class wyc_k198_stda_kzz(FactorGenerator):
	def __init__(self, *args, **kwargs):
		required_columns=['amount']
		super(wyc_k198_stda_kzz, self).__init__(*args, required_columns=required_columns, **kwargs)

	def on_bar(self, df):
		#收益率与成交额的相关性
		amount = df['amount'].between_time(data_morning_begin, trade_stop_time)
		amount = amount.groupby(amount.index.date).sum()
		amount.index = pd.to_datetime(amount.index)

		factor = ts_std(amount, 10)

		factor = factor.replace([np.inf, -np.inf], np.nan)

		factor = factor.iloc[-1].to_frame()
		columnname = self.__class__.__name__
		factor.columns = [columnname]
		return factor