from h5data.IO import IO
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20160101,20250630
in_sample_end_date = 20201231
start_date_ = int(s.tradingday(start_date,-250)[0])
end_date_ = int(s.tradingday(end_date,250)[-1])

# 读取更长区间的全市场数据
md = IO.read_data([start_date_, end_date_],columns=['pre_close', 'open', 'high', 'low', 'close', 'amt', 'adjfactor'], \
                   alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
ipo_data = IO.read_data([20000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
ipo_data = ipo_data.reset_index()
ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00','68'])]  # 筛选上交所和深交所股票
ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
ipo_data['dt'] = ipo_data['list_date']
ipo_data['is_list_date'] = True
ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date']]

md = md.join(ipo_data)
md['after_list'] = md['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
md.loc[md['amt'] == 0]['after_list'] = np.nan
md['list_len'] = md['after_list'].unstack().rolling(10000, 1).sum().stack()
md.loc[(md['list_len'].isnull() & (md['amt'] > 0)), 'list_len'] = 250
md['list_len'] = md['list_len'].unstack().fillna(method='ffill').stack()
md.loc[(md['list_len'] > 250), 'list_len'] = 250

md = md[md['amt']>0]
md_filtered = md[md.index.get_level_values(1).str.startswith(('60','30','00','68'))]

neptune_basic_file = md_filtered[['list_len']].loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
neptune_basic_file_in_sample = neptune_basic_file.loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(in_sample_end_date))]

# neptune_basic_file.to_pickle(f'/dfs/user/023859/neptune/basic_file_neptune_all_{start_date}_{end_date}.pkl')

public_factor_path_basic = f'/data/group/800463/data/projectZZmkt_public/factor_lib/Basic_closed_hf_finish_{start_date}_{in_sample_end_date}.h5'
local_factor_path_basic = f'/data/user/023859/factor_zooZZmkt/factor_lib/Basic_closed_hf_finish_{start_date}_{end_date}.h5'

if not os.path.exists(public_factor_path_basic):
    IO.pd_hdf5_writer(neptune_basic_file_in_sample, hdf5=public_factor_path_basic, dataset='neptune')
else:
    IO.pd_hdf5_writer(neptune_basic_file_in_sample, hdf5=public_factor_path_basic, dataset='neptune', override=True)

if not os.path.exists(local_factor_path_basic):
    IO.pd_hdf5_writer(neptune_basic_file, hdf5=local_factor_path_basic, dataset='neptune')
else:
    IO.pd_hdf5_writer(neptune_basic_file, hdf5=local_factor_path_basic, dataset='neptune', override=True)