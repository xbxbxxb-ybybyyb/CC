import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
def check_csv():
	error_list = {}
	root = 'S:\\Quant\\backtest\\local_data\\gogoal_htsc\\csv\\'
	file_list = os.listdir(root)
	for file in file_list:
		if file == 'stock_report_number':
			continue
		print(file)
		error_list[file] = []
		s_root = 'S:\\Quant\\backtest\\local_data\\gogoal_htsc\\csv\\' + file + '\\'
		date_list = os.listdir(s_root)
		date_list.sort()
		for date in date_list:
			if int(date[:-4]) < 20180327:
				continue
			s_path = s_root + date		
			d_path = 'Z:\\warehouse\\test\\gogoal_htsc\\' + file + '\\' + date
			df_s = pd.read_csv(s_path, encoding='gbk' ,header=0)
			df_d = pd.read_csv(d_path, header=0)
			df_s.fillna('NAN', inplace=True)
			df_d.fillna('NAN', inplace=True)
			s_ticker = []
			d_ticker = []
			for index, row in df_s.iterrows():
				ticker = row['Ticker']
				s_ticker.append(ticker)
			# print(s_ticker)
			for index, row in df_d.iterrows():
				ticker = str(row['Ticker'])
				if not ticker in s_ticker:
					d_ticker.append(ticker)
			if len(d_ticker) > 0:
				print(d_ticker)
				print(date)
			for ticker in d_ticker:
				df_d = df_d[df_d['Ticker'] != ticker]
			df_s.set_index('Ticker', inplace=True)
			df_d.set_index('Ticker', inplace=True)
			try:
				rst = df_d==df_s
				data_length = len(rst)
				rst = rst.sum()
				for i in rst:
					if i != data_length:
						print('-' * 10, date, file)
						print(rst)
						error_list[file].append(date)
						break
			except Exception as e:
				print(e)
				print(date)
				error_list[file].append(date)
	print(error_list)

def test():

	s_path = 'S:\\Quant\\backtest\\local_data\\gogoal_htsc\\csv\\con_forecast_stk\\20180417.csv'
	d_path = 'Z:\\warehouse\\test\\gogoal_htsc\\con_forecast_stk\\20180417.csv'
	df_s = pd.read_csv(s_path, encoding='gbk' ,header=0)
	df_d = pd.read_csv(d_path, header=0)
	df_s.fillna('NAN', inplace=True)
	df_d.fillna('NAN', inplace=True)
	# print(df_d['C13'])
	cmp_dict = {}
	# print(df_d)
	s_ticker = []
	d_ticker = []
	for index, row in df_s.iterrows():
		ticker = row['Ticker']
		s_ticker.append(ticker)
	# print(s_ticker)
	for index, row in df_d.iterrows():
		ticker = str(row['Ticker'])
		if not ticker in s_ticker:
			d_ticker.append(ticker)
	print(d_ticker)
	for ticker in d_ticker:
		df_d = df_d[df_d['Ticker'] != ticker]
	# rst = df_d==df_s
	# data_length = len(rst)
	# rst = rst.sum()
	df_s.set_index('Ticker', inplace=True)
	df_d.set_index('Ticker', inplace=True)
	rst = df_d == df_s
	data_length = len(rst)
	rst = rst.sum()
	print(rst)
if __name__ == '__main__':
	test()