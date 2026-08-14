import pandas as pd
import numpy as np
import IO
import decimal
import datetime
from xquant.factordata import FactorData
import os

s = FactorData()
# 2024 H1
start_date_ = '20231001'
end_date_ = '20241228'
f_data = IO.read_data([start_date_, end_date_],columns=['amt'],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_basicinfo = s.get_factor_value('WIND_AShareDescription')
list_2024 = list(df_basicinfo[df_basicinfo['S_INFO_LISTDATE'] >= '20240101']['S_INFO_WINDCODE'])
f_data = f_data.reset_index()
f_data = f_data[~f_data['Ticker'].str.contains('.BJ')]
f_data = f_data[~f_data['Ticker'].isin(list_2024)].set_index(['dt','Ticker'])
f_data = f_data[f_data['amt'] > 0] # 剔除当日无交易样本，否则xdb一直报error
#
os.system("pip uninstall xdbJG -y")
os.system("pip install /data/user/019073/marketdata/installer_and_demo/xdbJG-2.0.0-cp36-cp36m-linux_x86_64.whl")
from xdbJG.stockdata import StockData
xdb_datasource = StockData()

def get_kline1min(tradingday,result_path,basic_file_date):
    print(tradingday,'------start download k1min')
    res_date = pd.DataFrame()
    for index, row in basic_file_date.reset_index().iterrows():
        stock = row['Ticker']
        print(f'{tradingday}---{stock}')
        try:
            res_date = res_date.append(xdb_datasource.get_kline1m(tradingday,stock))
        except:
            print(f'error:{tradingday} {stock}')
    res_date.to_pickle(f'{result_path}{tradingday}.pkl')
    print(tradingday, f'------finish shape = {res_date.shape}')

from multiprocessing import Pool


pool = Pool(24)
task_list = []
result_path = '/dfs/user/015585/03_实习生数据/K1min_2024/'
for tradingday in s.tradingday(start_date_,end_date_):
    basic_file_date = f_data.loc[pd.Timestamp(tradingday):pd.Timestamp(tradingday)]
    task_list.append(pool.apply_async(get_kline1min,args=(tradingday,result_path,basic_file_date)))
pool.close()
pool.join()

