# -*- coding: utf-8 -*-
"""
Created on Mon Jan 15 13:17:25 2018

@author: 012315  013160
"""

import sys
from WindPy import w
import datetime as dt
import pandas as pd
import os
import numpy as np
from multifactor.IO import IO
from multifactor.IO.IO_enums import *
from log import Log
import config_reader
from utils import *

logger = Log('mapping_wind_htsc')

def get_root_keys(h5_store):
    '''
    --- DESCRIPTION ---
    Get group keys
    '''
    if type(h5_store) is pd.io.pytables.HDFStore:
        return ['/' + item for item in list(h5_store.root._v_groups.keys())]


def update_wind_qtr(cdate_list):
	qtr_list = get_qtr_list(cdate_list)
	factor_table = pd.read_excel('documents\\wind_mapping_without_cal.xlsx',header=0)
	save_path = config_reader.getConfig('root_path', 'csv_path')
	col_names = factor_table.columns.tolist()
	row_len = factor_table.shape[0]
	for i in range(row_len):
		dataset_name = factor_table.loc[i][col_names[0]]
		table_name = factor_table.loc[i][col_names[1]]
		factor_name = factor_table.loc[i][col_names[2]]
		retrieve_htsc(qtr_list, dataset_name, table_name, factor_name, save_path, 'FDD')
	# retrieve_htsc(qtr_list, 'yoyprofit', 'AShareAFIndicator', 'NET_PROFIT_YOY', save_path)

def retrieve_htsc(cdate_list, dataset_name, table_name, factor_name, save_path, type, over_ride_name=None):
	'''
	cdate_list is the date that should download
	dataset_name is the col name in the wind api
	factor_name is the col name in the htsc table
	table name is the table that contains the dataset
	if over_ride_name != None, will write the data in a new folder named over_ride_name
	save_path is the path store the csv file, it is stored in the config
	generally the save_path should be 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\wind_data\\'
	'''
	if over_ride_name !=None:
		save_folder = save_path + over_ride_name+'\\'
	else:
		save_folder = save_path + dataset_name+'\\'
	if not os.path.exists(save_folder):
		os.makedirs(save_folder)

	universe_folder = config_reader.getConfig('root_path', 'wind_stock_path')
	if type == 'FDD':
		h5_path = 'Z:\\warehouse\\prod\\FDD\\CHINA_STOCK\\QUARTERLY\\WIND\\'
	elif type == 'MD':
		h5_path = 'Z:\\warehouse\\prod\\MD\\CHINA_STOCK\\DAILY\\WIND\\'

	table_path = h5_path + 'WIND_' + table_name + '\\' + 'WIND_' + table_name + '.h5'
	logger.info('---' + dataset_name)
	print(table_name, factor_name)
	for date in cdate_list:
		stock_set = set()
		stock_list = pd.read_csv(universe_folder+str(date)+'.csv',header=0)['Ticker'].values.tolist()
		df = IO.read_data(date, columns = factor_name, alt = table_path)
		df.columns = [dataset_name]
		df.reset_index('dt', inplace = True)
		df.drop('dt', axis=1, inplace=True)
		exist_stock = df.index.values.tolist()
		stock_list = set(exist_stock) & set(stock_list)
		stock_list = list(stock_list)
		stock_list.sort()
		df = df.loc[stock_list]
		df.to_csv(save_folder+str(date)+'.csv')

def get_stock_list(cdate_list):
	cdate_list = [cdate_list] if type(cdate_list)!=list else cdate_list
	wind_stock_path = config_reader.getConfig('root_path', 'wind_stock_path')
	if not os.path.exists(wind_stock_path):
		os.makedirs(wind_stock_path)
	fdate_list = [int(i[:-4]) for i in os.listdir(wind_stock_path)]
	need_list = list(set(cdate_list) - set(fdate_list))
	logger.info('Need to download stock list for: ' + str(len(need_list)) + ' days')
	table_name = 'AShareEODPrices'
	h5_path = 'Z:\\warehouse\\prod\\MD\\CHINA_STOCK\\DAILY\\WIND\\'
	table_path = h5_path + 'WIND_' + table_name + '\\' + 'WIND_' + table_name + '.h5'
	for date in need_list:
		df = IO.read_data(need_list, columns='OBJECT_ID', alt = table_path)
		df.reset_index('dt', inplace = True)
		stock_list = df.index.values.tolist()
		df = pd.DataFrame(stock_list, columns=['Ticker'])
		df.to_csv(wind_stock_path+str(date) + '.csv', index = False)


def get_qtr_list(end_date=None,num_qtr=3):
	end_date = end_date[-1] if type(end_date)==list else end_date
	if end_date == None:
		end_date = get_current_date(new_date_time=18)

	if end_date< 20090105:
		last_day = 20090105
	else:
		last_day = end_date

	year_list = [str(i) for i in range(2000,1200)]
	month_date = ['0331','0630','0930','1231']
	date_list_complete = [i+j for i in year_list for j in month_date]
	qtr_list = [int(i) for i in date_list_complete if int(i)<=last_day][-1*num_qtr:]
	get_stock_list(qtr_list)
	return qtr_list

def get_root_keys(h5_store):
    '''
    --- DESCRIPTION ---
    Get group keys
    '''
    if type(h5_store) is pd.io.pytables.HDFStore:
        return ['/' + item for item in list(h5_store.root._v_groups.keys())]

def test_secu(cdate_list):
	tmp_h5_path = 'S:\\Quant\\data\\secuMain\\CHINA_STOCK\\WIND\\secuMain_CHINA_STOCK_WIND.h5'
	with pd.HDFStore(tmp_h5_path, 'r') as h5_store:
		keys = get_root_keys(h5_store)
		for key in keys:
			df_test = h5_store.select(key)
			# df_test.reset_index('dt', inplace=True)
			print(df_test)
	# date = cdate_list[-1]
	# universe_folder = config_reader.getConfig('root_path', 'wind_stock_path')
	# stock_list = pd.read_csv(universe_folder+str(date)+'.csv',header=0)['Ticker'].values.tolist()
	h5_path = 'Z:\\warehouse\\prod\\ETC\\CHINA_STOCK\\DAILY\\WIND\\'
	table_name = 'AShareDescription'
	table_path = h5_path + 'WIND_' + table_name + '\\' + 'WIND_' + table_name + '.h5'
	df = IO.read_data([20090101,21000101],columns=['S_INFO_DELISTDATE', 'S_INFO_LISTDATE'],alt = table_path)
	df.reset_index('dt', inplace=True)
	df.drop('dt', axis=1, inplace=True)
	# df.reset_index('Ticker', inplace=True)
	Ticker_list = list(df.index.values)
	delist_Ticker = []
	for ticker in Ticker_list:
		if not ticker[0].isdigit():
			delist_Ticker.append(ticker)
		elif ticker[0] == '9':
			delist_Ticker.append(ticker)
	Ticker_list = list(set(Ticker_list) - set(delist_Ticker))
	df.reset_index('Ticker', inplace=True)
	df = df[df['Ticker'].isin(Ticker_list)]
	df.set_index('Ticker', inplace=True)
	df.columns=['ipo_date', 'delist_date']
	df.fillna(20991231, inplace=True)
	df['ipo_date'] = df['ipo_date'].apply(lambda x: dt.datetime.strptime(str(int(x)),'%Y%m%d'))
	df['delist_date'] = df['delist_date'].apply(lambda x: dt.datetime.strptime(str(int(x)),'%Y%m%d'))
	print(df)


if __name__ == '__main__':
	cdate_list = [20180723]
	test_secu(cdate_list)
