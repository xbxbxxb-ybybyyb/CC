import pandas as pd
import numpy as np
import IO
import decimal
import datetime
from xquant.factordata import FactorData

s = FactorData()
# 2018-2019，向前多存2个月用于ROLLING因子
start_date_ = '20171001'
end_date_ = '20191231'
f_data = IO.read_data([start_date_, end_date_],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
path = '/dfs/user/015585/03_实习生数据/md_2018_2020/'
with pd.HDFStore(path + f'MD_{start_date_}_{end_date_}.h5') as h5_store:
    h5_store.put('data', f_data, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()

# 2020
start_date_ = '20200101'
end_date_ = '20201231'
f_data = IO.read_data([start_date_, end_date_],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
path = '/dfs/user/015585/03_实习生数据/md_2018_2020/'
with pd.HDFStore(path + f'MD_{start_date_}_{end_date_}.h5') as h5_store:
    h5_store.put('data', f_data, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()

# 2024 H1
start_date_ = '20231001'
end_date_ = '20240630'
f_data = IO.read_data([start_date_, end_date_],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_basicinfo = s.get_factor_value('WIND_AShareDescription')
list_2024 = list(df_basicinfo[df_basicinfo['S_INFO_LISTDATE'] >= '20240101']['S_INFO_WINDCODE'])
f_data = f_data.reset_index()
f_data = f_data[~f_data['Ticker'].str.contains('.BJ')]
f_data = f_data[~f_data['Ticker'].isin(list_2024)].set_index(['dt','Ticker'])
path = '/dfs/user/015585/03_实习生数据/md_2024/'
with pd.HDFStore(path + f'MD_{start_date_}_{end_date_}.h5') as h5_store:
    h5_store.put('data', f_data, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()

# 2024 H2
start_date_ = '20240701'
end_date_ = '20241228'
f_data = IO.read_data([start_date_, end_date_],
                      alt='/data/group/800080/warehouse/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
df_basicinfo = s.get_factor_value('WIND_AShareDescription')
list_2024 = list(df_basicinfo[df_basicinfo['S_INFO_LISTDATE'] >= '20240101']['S_INFO_WINDCODE'])
f_data = f_data.reset_index()
f_data = f_data[~f_data['Ticker'].str.contains('.BJ')]
f_data = f_data[~f_data['Ticker'].isin(list_2024)].set_index(['dt','Ticker'])
path = '/dfs/user/015585/03_实习生数据/md_2024/'
with pd.HDFStore(path + f'MD_{start_date_}_{end_date_}.h5') as h5_store:
    h5_store.put('data', f_data, format='table', append=False, data_columns=True)
    h5_store.get_storer('data').attrs.modification_date = datetime.datetime.today()


tmp = pd.read_hdf('/dfs/user/015585/03_实习生数据/md_2024/MD_20240701_20241228.h5')