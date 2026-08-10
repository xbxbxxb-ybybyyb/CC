import json
import multiprocessing
import os
import pandas as pd
from joblib import Parallel, delayed
from loguru import logger

from common.query_service import *
from common.tools import *
from params.templates import *

index_list = ['SZ50', 'HS300', 'ZZ500', 'ZZ1000']

ashare_total = factor_query_service.get_factor_value \
	('WIND_AShareCapitalization', factors=['S_INFO_WINDCODE', 'CHANGE_DT', 'FLOAT_A_SHR']).rename(
	columns={'S_INFO_WINDCODE': 'Ticker'}).set_index('Ticker')

ashare_total['CHANGE_DT'] = ashare_total['CHANGE_DT'].astype('int')


def get_shares(stock, trading_day):
	temp = ashare_total.loc[stock].reset_index(drop=True).sort_values(by='CHANGE_DT')
	if stock == '689009.SH' and temp.loc[temp['CHANGE_DT'] <= int(trading_day)].iloc[-1][
		'FLOAT_A_SHR'] < 10000:
		return [stock, temp.loc[temp['CHANGE_DT'] <= int(trading_day)].iloc[-1]['FLOAT_A_SHR'] * 10]
	else:
		return [stock, temp.loc[temp['CHANGE_DT'] <= int(trading_day)].iloc[-1]['FLOAT_A_SHR']]


class ParamsGenerator:

	def __init__(self):
		self.thread_num = "40"
		self.params_template = template_backend_params

	def get_future_trading_instruments(self, trading_day):
		start_date = trading_day
		end_date = trading_day
		result_IH = future_query_service.get_instrument_all("IH", start_date, end_date)
		result_IH = sorted(result_IH)
		result_IF = future_query_service.get_instrument_all("IF", start_date, end_date)
		result_IF = sorted(result_IF)
		result_IC = future_query_service.get_instrument_all("IC", start_date, end_date)
		result_IC = sorted(result_IC)
		result_IM = future_query_service.get_instrument_all("IM", start_date, end_date)
		result_IM = sorted(result_IM)
		result = result_IH + result_IF + result_IC + result_IM
		final_res = []
		for sym in result:
			final_res.append(sym[:6])
		return final_res

	def get_index_constituent_stock(self, variety, trading_day):
		stocks = []
		res = factor_query_service.hset('INDEX', trading_day, variety, weightType=1)
		for index, row in res.iterrows():
			stocks.append(row['stock'])
		return stocks

	def getType(self, index_type):
		if index_type == "SZ50":
			return "IH"
		if index_type == "HS300":
			return "IF"
		if index_type == "ZZ500":
			return "IC"
		if index_type == "ZZ1000":
			return "IM"

	def get_index_weight(self, parse_date, index_list=index_list):
		df_res_list = []
		for index_type in index_list:
			df = factor_query_service.hset("INDEX", parse_date, index_type, weightType=1)
			df = df.reset_index()
			index_type_name = self.getType(index_type)
			df['type'] = index_type_name
			df['date'] = parse_date
			df = df.rename(columns={'stock': 'symbol'})
			df = df[['date', 'symbol', 'type', 'weight']]
			df_res_list.append(df)
		res = pd.concat(df_res_list)
		index_weight = json.loads(res.to_json(orient='records', double_precision=15))
		return index_weight

	def get_adjfactor(self, parse_date, stock_list):
		ashareeodprices = factor_query_service.get_factor_value('WIND_AShareEODPrices',
		                                                        factors=['S_INFO_WINDCODE', 'S_DQ_ADJFACTOR'],
		                                                        trade_dt=[parse_date])
		adjfactor_df = ashareeodprices.set_index('S_INFO_WINDCODE').loc[
			list(set(stock_list) - {'689009.SH'})].reset_index()
		adjfactor_df = adjfactor_df.append(
			pd.Series({'S_INFO_WINDCODE': '689009.SH', 'S_DQ_ADJFACTOR': 1, 'dt': parse_date}), ignore_index=True)
		adjfactor_df['dt'] = parse_date
		return adjfactor_df

	def get_constituent_stock_info(self, stock_list, trading_day):
		results = Parallel(n_jobs=10, backend=multiprocessing)(delayed(get_shares)(i, trading_day) for i in stock_list)
		float_shares_df = pd.DataFrame(results, columns=['Ticker', 'float_shares'])

		all_date_list = [trading_day]
		adjfactor_df_list = []
		for d in all_date_list:
			temp = self.get_adjfactor(d, stock_list)
			adjfactor_df_list.append(temp)
		adjfactor_df = pd.concat(adjfactor_df_list)
		adjfactor_df['dt'] = adjfactor_df['dt'].astype('datetime64[ns]')
		adjfactor_df['S_DQ_ADJFACTOR'] = adjfactor_df['S_DQ_ADJFACTOR'].fillna(1)
		adjfactor_df = adjfactor_df.rename(
			columns={'S_DQ_ADJFACTOR': 'adjfactor', 'S_INFO_WINDCODE': 'stock', 'dt': 'mddate'})
		adjfactor_df = adjfactor_df.set_index(['mddate', 'stock'])
		close_df = factor_query_service.get_factor_value("Basic_factor", stock_list, all_date_list, ['close'])
		close_df = close_df.reset_index()
		close_df['mddate'] = close_df['mddate'].astype('datetime64[ns]')
		close_df = close_df.set_index(['mddate', 'stock'])
		close_adjfactor_df = pd.concat([adjfactor_df, close_df], axis=1)
		close_adjfactor_df = close_adjfactor_df.xs('{} 00:00:00'.format(format_date(trading_day)), level=0)
		if float_shares_df['float_shares'].isnull().any():
			logger.error("float_shares字段存在空值, 请重新生成")
		constituent_stock_info = pd.concat([float_shares_df.set_index(['Ticker']), close_adjfactor_df], axis=1)
		constituent_stock_info = constituent_stock_info.reset_index()
		# 策略参数生成完成需要校验一下, 检查float_shares等字段是否不为null, 可能出现查询太早导致查询结果为null的情况
		constituent_stock_info = constituent_stock_info.rename(
			columns={"index": "Ticker", "adjfactor": "pre_adjfactor", "close": "pre_close"})
		res = json.loads(constituent_stock_info.to_json(orient='records', double_precision=15))
		return res

	def add_stock_list(self, res: list, to_add):
		help_set = set(res)
		for i in to_add:
			if i not in help_set:
				res.append(i)
				help_set.add(i)
		return res

	def generate(self, next_trading_day):
		params = self.params_template.copy()
		params['交易日期'] = str(next_trading_day)
		his_dates = factor_query_service.tradingday(next_trading_day, -7)
		params['历史数据交易日列表'] = his_dates[:-1]
		params['期货代码列表'] = self.get_future_trading_instruments(next_trading_day)
		hs300_stock_list = self.get_index_constituent_stock('HS300', next_trading_day)
		zz500_stock_list = self.get_index_constituent_stock('ZZ500', next_trading_day)
		zz1000_stock_list = self.get_index_constituent_stock('ZZ1000', next_trading_day)
		sh50_stock_list = self.get_index_constituent_stock('SH50', next_trading_day)
		params['沪深300标的列表'] = hs300_stock_list
		params['中证500标的列表'] = zz500_stock_list
		params['中证1000标的列表'] = zz1000_stock_list
		params['上证50标的列表'] = sh50_stock_list
		params['成分股权重列表'] = self.get_index_weight(next_trading_day)
		stock_list = []
		self.add_stock_list(stock_list, hs300_stock_list)
		self.add_stock_list(stock_list, zz500_stock_list)
		self.add_stock_list(stock_list, zz1000_stock_list)
		self.add_stock_list(stock_list, sh50_stock_list)
		pre_trading_day = factor_query_service.tradingday(next_trading_day, -2)[0]
		params['成分股信息'] = self.get_constituent_stock_info(stock_list, pre_trading_day)
		return json.dumps(params, indent=4, ensure_ascii=False)

	def generate_frontend(self, date, filepath):
		frontend_params = template_frontend_params.copy()
		# frontend_params['参数地址'] = filepath
		frontend_params['path'] = filepath
		frontend_content = json.dumps(frontend_params, indent=4, ensure_ascii=False)
		return frontend_content


def write_params_file(base_path, next_trading_day, backend_params_filepath = None):
	params_generator = ParamsGenerator()
	content = params_generator.generate(next_trading_day)
	date_dir_path = os.path.join(base_path, next_trading_day)
	if not os.path.exists(date_dir_path):
		os.makedirs(date_dir_path)
	filepath = os.path.join(date_dir_path, "settings.json")
	serialize_to_file(content, filepath)
	if backend_params_filepath is not None:
		filepath = backend_params_filepath
	frontend_content = params_generator.generate_frontend(next_trading_day, filepath)
	frontend_filepath = os.path.join(date_dir_path, "params.json")
	serialize_to_file(frontend_content, frontend_filepath)


if __name__ == "__main__":
	# testcase_base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
	base_path = "/data/user/018728/cpp_projects/csi_calculator/testcase"
	write_params_file(base_path, "20230615")
