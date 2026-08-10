from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pandas as pd
pd.set_option('display.width', 5000)
import numpy as np
import os
# from utils.sigutils import *

class FactorGeneratorComplex:
	__data__ = None
	__ticker__=None
	def __init__(self, factor_name='test', lookback_bars=5000, required_columns=None,
				 savepath='/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE'):
		self.factor_name = factor_name
		self.lookback_bars = lookback_bars
		self.required_columns = required_columns
		self.savepath = savepath

	def pd_writer(self, sig, savepath):
		sig_name = sig.columns[0]
		file_name = os.path.join(savepath, sig_name + '.h5')
		if os.path.exists(file_name):
			sigold = IO.read_data(alt=file_name)
			sigold = sigold[~sigold.index.isin(sig.index)]
			signew = pd.concat([sigold, sig], axis=0).sort_index()
			override = True
		else:
			signew = sig
			override = None
		IO.pd_hdf5_writer(signew, file_name, sig_name, override=override, append=None)

	def pd_writer2(self, sig, savepath):
		sig_name = sig.columns[0]
		file_name = os.path.join(savepath, sig_name + '.h5')
		if os.path.exists(file_name):
			sigold = IO.read_data(alt = file_name)
			sigold = sigold[~sigold.index.isin(sig.index)]
			signew = pd.concat([sigold,sig],axis=0).sort_index()
			override = True
			IO.pd_hdf5_writer(signew, file_name,sig_name, override=override,append = None)

	@classmethod
	def prepare_hot_data(inst, start_date, end_date, use_cache = True, save_cache = False, ticker='IC.CFE'):
		inst.__ticker__ = ticker
		cache_path = '/data/user/012398/data/cache'
		if not os.path.exists(cache_path):
			os.makedirs(cache_path)
		cache_name = os.path.join(cache_path,'IC_complex.pkl')
		if use_cache:
			pass
			# inst.__data__ = read_pickle(cache_name)
		else:
			data_dict = {}
			data_path = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/'
			start_date = IO.str_date_parser(start_date)
			end_date = IO.str_date_parser(end_date)
			index_data = IO.read_data([start_date, end_date],alt=os.path.join(data_path,'MD_STOCK_INDEX_SPOT_MINUTE.h5')).xs(ticker,level=1).sort_index()
			futures_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path,'MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')).xs(ticker, level=1).sort_index()
			cfg_stocks_data = IO.read_data([start_date, end_date], alt=os.path.join(data_path, 'IC_STOCKS_MINUTE_DATA.h5')).unstack().sort_index()
			#data = index_data
			data = pd.concat([index_data, futures_data], axis=1).sort_index()
			cfg = cfg_stocks_data.reindex(data.index)

			for d in [data, cfg]:
				for col in d.columns.get_level_values(0).unique():
					data_dict[col] = d[col]

			inst.__data__ = data_dict
			# if save_cache:
				# save_pickle(data_dict, cache_name)

	def slicer(self):
		return {col:self.__data__[col].copy() for col in self.required_columns}

	def __callback__(self, start_date, end_date):
		data = self.slicer()
		savepath = os.path.join(self.savepath, 'IC_prod')
		if not os.path.exists(savepath):
			os.makedirs(savepath)
		factor = self.on_bar(data)
		assert len(factor) == data[self.required_columns[0]].shape[0]
		factor['Ticker'] = self.__ticker__
		start_date = IO.str_date_parser(start_date)
		end_date = udt.get_trading_day_offset(end_date, 1)[0]
		factor = factor.loc[start_date:end_date]
		factor = factor.reset_index().set_index(['dt', 'Ticker'])
		self.pd_writer(factor, savepath)
		self.pd_writer2(factor,'/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IC_prod_20200826')