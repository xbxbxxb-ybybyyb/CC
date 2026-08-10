from multifactor.IO import IO
from multifactor.IO.IO_enums import *
import multifactor.utility.dt as udt
import pandas as pd
import numpy as np
import os

class FactorGenerator:
	__data__ = None
	__ticker__=None
	def __init__(self, factor_name = 'test', lookback_bars = 5000, required_columns = None,
				 savepath = '/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE'):
		self.factor_name = factor_name
		self.lookback_bars = lookback_bars
		self.required_columns = required_columns
		self.savepath = savepath

	def pd_writer(self, sig, savepath):
		sig_name = sig.columns[0]
		file_name = os.path.join(savepath, sig_name + '.h5')
		if os.path.exists(file_name):
			sigold = IO.read_data(alt = file_name)
			sigold = sigold[~sigold.index.isin(sig.index)]
			signew = pd.concat([sigold,sig],axis=0).sort_index()
			override = True
		else:
			signew = sig
			override = None
		IO.pd_hdf5_writer(signew, file_name,sig_name, override=override,append = None)

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
	def prepare_hot_data(inst, start_date, end_date, ticker='IC.CFE'):
		inst.__ticker__=ticker
		start_date = IO.str_date_parser(start_date)
		end_date = IO.str_date_parser(end_date)
		index_data = IO.read_data([start_date,end_date],alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_SPOT_MINUTE.h5')
		futures_data = IO.read_data([start_date,end_date],alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_MINUTE_MAIN.h5')
		#tick2minute_data = IO.read_data([start_date,end_date],alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_FUTURES_TICK_TO_MINUTE.h5')
		#cfg_data = IO.read_data([start_date,end_date],alt = '/data/user/015626/data/share/MD/CHINA_FUTURES/MINUTE/MD_STOCK_INDEX_CFG_MINUTE.h5')

		data = pd.concat([index_data, futures_data],axis=1).xs(ticker,level=1).sort_index()
		ifdata = futures_data.xs('IF.CFE',level=1)
		ifdata.columns = [col + '_if' for col in ifdata.columns]
		ihdata = futures_data.xs('IH.CFE',level=1)
		ihdata.columns = [col + '_ih' for col in ihdata.columns]
		
		ifdata_spot = index_data.xs('IF.CFE',level=1)
		ifdata_spot.columns = [col + '_if' for col in ifdata_spot.columns]
		ihdata_spot = index_data.xs('IH.CFE',level=1)
		ihdata_spot.columns = [col + '_ih' for col in ihdata_spot.columns]
		data = data.join(ifdata).join(ihdata).join(ifdata_spot).join(ihdata_spot)

		# for col in ['open','high','low','close','open_spot','high_spot','low_spot','close_spot',
		# 			'open_if','high_if','low_if','close_if','open_spot_if','high_spot_if','low_spot_if','close_spot_if',
		# 			'open_ih','high_ih','low_ih','close_ih','open_spot_ih','high_spot_ih','low_spot_ih','close_spot_ih']:
		# 	data[col] = data[col].fillna(method='pad')

		inst.__data__ = data

	def slicer(self):
		return self.__data__[self.required_columns].copy()


	def __callback__(self, start_date,end_date):
		data = self.slicer()
		savepath = os.path.join(self.savepath, 'IC_prod')
		if not os.path.exists(savepath):
			os.makedirs(savepath)
		factor = self.on_bar(data)

		assert len(factor) == data.shape[0]
		factor['Ticker'] = self.__ticker__
		start_date = IO.str_date_parser(start_date)
		end_date = udt.get_trading_day_offset(end_date,1)[0]
		factor = factor.loc[start_date:end_date]
		factor = factor.reset_index().set_index(['dt','Ticker'])
		self.pd_writer(factor, savepath)
		self.pd_writer2(factor,'/data/user/012398/data/alpha/CHINA_FUTURES/MINUTE/IC_prod_20200826')