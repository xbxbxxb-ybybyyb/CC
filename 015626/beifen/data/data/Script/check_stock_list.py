import os
import csv
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
def check_stock_list(date, factor):
	stock_list = []
	path = 'D:\\Quant\\backtest\\local_data\\wind_data\\'
	path = path + factor + '\\' + str(date) + '.csv';
	if not os.path.exists(path):
		return stock_list
	d = pd.read_csv(path, header=0)
	for index , row in d.iterrows():
		if pd.isnull(row.longdebttolongcaptial):
			stock_list.append(row.Ticker)
	return stock_list

if __name__ == '__main__':
	stock_list = check_stock_list(20180330, 'longdebttolongcaptial')
	print(len(stock_list))