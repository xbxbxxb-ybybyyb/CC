from multifactor.IO import IO
import multifactor.utility.dt as udt
import pandas as pd
import numpy as np
import os

class FactorGenerator:
	__data_spot__ = None
	__data_all__ = None
	__data_index__ = None
	__ticker__ = None
	def __init__(self, factor_name = 'test', lookback_bars = 5000, required_columns = None,
				 savepath = '/data/user/015626/data/share/factor/1min/IC_factors'):
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


	@classmethod
	def prepare_hot_data(inst, start_date, end_date, future_kind = 'contract_00', ticker = 'IC.CFE'):
		"""
		:param start_date:
		:param end_date:
		:param future_kind: future_kind表示期货种类，contract_00表示近月合约，contract_main表示主力合约
		:param ticker: 生成因子种类，筛选index时使用
		"""
		datapath = '/data/user/015626/data/share/MD/CHINA_FUTURES/'
		spotdata_name = 'MD_STOCK_INDEX_SPOT_MINUTE.h5'
		contractdata_name = 'MD_STOCK_INDEX_FUTURES_MINUTE_ALL_CONTRACT.h5'
		indexdata_name = 'MD_STOCK_INDEX_FUTURES_UNIVERSE.h5'
		start_date = IO.str_date_parser(start_date)
		end_date = IO.str_date_parser(end_date)
		spot_data = IO.read_data([start_date,end_date],alt = os.path.join(datapath,'MINUTE',spotdata_name))

		icdata_spot = spot_data.xs('IC.CFE',level=1)
		ifdata_spot = spot_data.xs('IF.CFE',level=1)
		ifdata_spot.columns = [col + '_if' for col in ifdata_spot.columns]
		ihdata_spot = spot_data.xs('IH.CFE',level=1)
		ihdata_spot.columns = [col + '_ih' for col in ihdata_spot.columns]
		spot_data = icdata_spot.join(ifdata_spot).join(ihdata_spot)

		futures_data = IO.read_data([start_date, end_date], alt=os.path.join(datapath,'MINUTE',contractdata_name))
		futures_data = futures_data.reset_index()
		futures_data['contract'] = futures_data.Ticker.apply(lambda x: x[2:])
		futures_data['Ticker'] = futures_data.Ticker.apply(lambda x: x[:2] + x[-4:])
		futures_data = futures_data.set_index(['dt', 'contract', 'Ticker'])

		all_data = {}
		for x in futures_data.index.get_level_values(1).unique().tolist():
			df1 = futures_data.xs(x, level=1)
			nowdata = pd.DataFrame()
			for y in df1.index.get_level_values(1).unique().tolist():
				df2 = df1.xs(y, level=1)
				if y[:2] in ['IF', 'IH']:
					df2 = df2.rename(columns={i: i + '_' + y[:2].lower() for i in df2.columns.tolist()})
				nowdata = df2 if len(nowdata) == 0 else nowdata.join(df2)
			all_data[x] = nowdata.join(spot_data, how = 'left')

		indexdf = IO.read_data([start_date, end_date], alt = os.path.join(datapath,'daily',indexdata_name))
		indexdf = indexdf.xs(ticker, level = 1)[[future_kind]]
		t_days_list = udt.get_trading_date_range(str(indexdf.index[0].date()).replace('-', ''), str(indexdf.index[-1].date()).replace('-', ''))
		t_days_list = [str(i)[:10] for i in t_days_list]
		t_mins_list = pd.date_range('09:30:00', '11:29:00', freq='min').to_list() + pd.date_range('13:00:00', '14:57:00', freq='min').to_list()
		t_mins_list = [str(i)[-8:] for i in t_mins_list]
		index_list = []
		for d in t_days_list:
			for m in t_mins_list:
				index_list.append(d + ' ' + m)
		index_min = pd.DataFrame({'dt': index_list})
		index_min['dt'] = pd.to_datetime(index_min['dt'])
		index_min['date'] = index_min['dt'].apply(lambda x: x.date())
		index_min['date'] = pd.to_datetime(index_min['date'])

		indexdf['Ticker'] = indexdf[future_kind].apply(lambda x: x[2:])
		indexdf = indexdf.reset_index().rename(columns={'dt': 'date'})
		indexdf = pd.merge(indexdf, index_min, on='date')
		indexdf = indexdf[['dt', 'Ticker']].set_index(['dt', 'Ticker'])

		inst.__data_spot__ = spot_data
		inst.__data_all__ = all_data
		inst.__data_index__ = indexdf
		inst.__ticker__ = ticker

	def __callback__(self, start_date, end_date):
		savepath = os.path.join(self.savepath, 'IC_prod_main')
		if not os.path.exists(savepath):
			os.makedirs(savepath)

		# required_columns do not contains future data
		if np.all(['spot' in x for x in self.required_columns]):
			data = self.__data_spot__[self.required_columns].copy()
			factor = self.on_bar(data)
		else:
			factor = pd.DataFrame()
			for key in self.__data_all__.keys():
				data = self.__data_all__[key].copy()
				if len(data) < (11 * 238):
					continue
				temp_factor = self.on_bar(data).reset_index()
				temp_factor['Ticker'] = key
				temp_factor = temp_factor.set_index(['dt','Ticker'])
				factor = factor.append(temp_factor)

			factor = self.__data_index__.join(factor, how = 'inner').reset_index(level = 1, drop = True).sort_index()

		assert len(factor) == self.__data_spot__.shape[0]
		factor['Ticker'] = self.__ticker__
		start_date = IO.str_date_parser(start_date)
		end_date = udt.get_trading_day_offset(end_date,1)[0]
		factor = factor.loc[start_date:end_date]
		factor = factor.reset_index().set_index(['dt','Ticker'])
		self.pd_writer(factor, savepath)
