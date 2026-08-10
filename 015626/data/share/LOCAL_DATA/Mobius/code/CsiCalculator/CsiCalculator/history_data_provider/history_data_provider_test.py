import os
import pandas as pd


if __name__ == "__main__":
	# pd.set_option('display.max_columns', 1000)
	pd.set_option('display.max_rows', 1000)
	# pd.set_option('display.width', 1000)

	base_path = r"/data/group/800466/warehouse/prod/MD/MarketData/MD/"
	stock_base_path = os.path.join(base_path, 'CHINA_STOCK/MINUTE')
	future_base_path = os.path.join(base_path, 'CHINA_FUTURES/MINUTE/backup')
	index_base_path = os.path.join(base_path, 'CHINA_INDEX/MINUTE')
	stock_h5_filepath = os.path.join(stock_base_path, '688680.SH.h5')
	future_h5_filepath = os.path.join(future_base_path, 'IC_MINUTE.h5')
	index_h5_filepath = os.path.join(index_base_path, '000852.SH.h5')
	df1 = pd.read_hdf(stock_h5_filepath)
	df2 = pd.read_hdf(future_h5_filepath)
	df3 = pd.read_hdf(index_h5_filepath)
	print(df1[-1422:])
	print(df2[-1440 * 4:])
	print(df3[-1422:])

