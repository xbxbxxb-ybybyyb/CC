from h5data.IO import IO
import pandas as pd
import numpy as np
from tqdm import tqdm
import os
from xquant.factordata import FactorData
s = FactorData()

def generate_neptune_basic_stocks_pool(start_date, end_date):
    zz1000 = IO.read_data([start_date, end_date], columns=['index_1000'],
                          alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
    trading_days = s.tradingday(start_date, end_date)
    res = {}
    for date in tqdm(trading_days):
        if date < '20170101':
            zz1000_list = list(zz1000[zz1000['index_1000']].loc[pd.to_datetime(date)].index)
            stockPool = list(set(zz1000_list))
        else:
            stockPool = list(set(s.hset('INDEX', date, 'ZZ1000')['stock']))
        res[date] = stockPool
    return res

start_date, end_date = 20160101,20250630
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
index_available_dict = generate_neptune_basic_stocks_pool(start_date, end_date)

mi_tuples = []
for date, stock_list in index_available_dict.items():
    for stock in stock_list:
        mi_tuples.append((pd.to_datetime(date), stock))

filter_idx = pd.MultiIndex.from_tuples(mi_tuples, names=md.index.names)
md_filtered = md.loc[md.index.intersection(filter_idx)]
md_filtered = md_filtered.sort_index()

neptune_basic_file = md_filtered[['list_len']]
neptune_basic_file.to_pickle('/dfs/user/023859/share_file/for_sss/basic_file_zz1000_20160101_20250630.pkl')
# public_factor_path_basic = f'/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_{start_date}_{end_date}_tmp.h5'
# if not os.path.exists(public_factor_path_basic):
#     IO.pd_hdf5_writer(neptune_basic_file, hdf5=public_factor_path_basic, dataset='neptune')
# else:
#     IO.pd_hdf5_writer(neptune_basic_file, hdf5=public_factor_path_basic, dataset='neptune', override=True)