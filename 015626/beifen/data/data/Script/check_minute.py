import pandas as pd
import os
import pickle
def filter_date(test_df):
	test_df.reset_index('Ticker', inplace=True)
	test_df = test_df.loc[date]
	test_df.reset_index('dt', inplace=True)
	test_df.drop(['dt', 'Ticker'], axis = 1, inplace=True)
	return test_df
	
def check_minute(date):
	test_root = 'Z:\\warehouse\\test\\minute_XQuant\\stock\\'
	target_root = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock\\'
	dict_rst = {}
	for file in os.listdir(test_root):
		if not file in os.listdir(target_root):
			print(file, 'not in target_df')
		test_pickle_file = test_root + file
		target_pickle_file = target_root + file
		try:
			test_df = pd.read_pickle(test_pickle_file, compression = 'gzip')
			test_df.reset_index('Ticker',inplace=True)
			test_df.fillna(0,inplace=True)
			target_df = pd.read_pickle(target_pickle_file, compression = 'gzip')
			target_df.reset_index('Ticker',inplace=True)
			target_df.fillna(0,inplace=True)
			rst = test_df.loc[date] != target_df.loc[date]
			total = rst.sum().sum()
			if total > 5:
				print(file)
				print(total)
				dict_rst[file] = total
			# target_dict = {}
			# col_list = target_df.columns.values
			# for index, row in target_df.iterrows():
			# 	for col in col_list:
			# 		if col == 'amt':
			# 			continue
			# 		if abs(row[col] - test_df.loc[index][col]) > 0.001:
			# 			print(file, col, index, row[col], test_df.loc[index][col])
		except Exception as e:
			print(e)
			print(file)
	print(dict_rst)
	with open('D:\\minute_check.pickle','wb') as file:
		pickle.dump(dict_rst, file)

def test():
	test = 'Z:\\warehouse\\prod\\LOCAL_DATA\\CSV\\WIND\\MINUTE\\stock\\UnAdjstedStockMinute_000029.pkl'
	df = pd.read_pickle(test, compression = 'gzip')
	print(df)


if __name__ == '__main__':
	date = 20190327
	# test()
	check_minute(20190327)
	check_minute(20190326)
	check_minute(20190325)

# dat_exist_stk = pd.read_pickle(pickle_file,compression='gzip')