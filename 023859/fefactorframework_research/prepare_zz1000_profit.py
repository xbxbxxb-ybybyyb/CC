import pandas as pd
from tqdm import tqdm
from xquant.factordata import FactorData
s = FactorData()
from h5data.IO import IO
import os

start_date, end_date = 20170110, 20250630
basic = pd.read_pickle('/dfs/user/023859/share_file/for_sss/basic_file_zz1000_20160101_20250630.pkl').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
res_path = '/dfs/user/023859/share_file/for_skk/neptune/zz1000_profit_interval_20170110_20250630.h5'
trading_days = s.tradingday(start_date, end_date)

ZZ1000_weight = []
for date in tqdm(trading_days):
    df_ZZ1000 = s.hset('INDEX',date,'ZZ1000',weightType=1) # 选择预估权重，避免回测用到未来数据
    if date < '20191216':
        last_date = int(s.tradingday(date, -2)[0])
        last_df_ZZ1000 = s.hset('INDEX', last_date, 'ZZ1000', weightType=0)
        df_ZZ1000 = pd.concat([df_ZZ1000,last_df_ZZ1000[last_df_ZZ1000['stock']=='000043.SZ']],ignore_index=True)
    if date < '20181226':
        last_date = int(s.tradingday(date, -2)[0])
        last_df_ZZ1000 = s.hset('INDEX', last_date, 'ZZ1000', weightType=0)
        df_ZZ1000 = pd.concat([df_ZZ1000,last_df_ZZ1000[last_df_ZZ1000['stock']=='000022.SZ']],ignore_index=True)

    ZZ1000_weight_date = pd.DataFrame(index = df_ZZ1000['stock'])
    ZZ1000_weight_date.index.names = ['stock']
    ZZ1000_weight_date['weight'] = df_ZZ1000.set_index('stock')['weight']/100
    ZZ1000_weight_date = ZZ1000_weight_date.reset_index()
    ZZ1000_weight_date['dt'] = pd.Timestamp(date)
    ZZ1000_weight_date = ZZ1000_weight_date.rename(columns={'stock':'Ticker'})
    ZZ1000_weight_date = ZZ1000_weight_date.set_index(['dt','Ticker'])[['weight']]
    ZZ1000_weight.append(ZZ1000_weight_date)

ZZ1000_weight = pd.concat(ZZ1000_weight, axis=0)
basic['buy_amt'] = 5e8*ZZ1000_weight['weight']

assert basic['buy_amt'].isnull().sum() == 0

if not os.path.exists(res_path):
    IO.pd_hdf5_writer(basic[['buy_amt']], hdf5=res_path, dataset='neptune')
else:
    IO.pd_hdf5_writer(basic[['buy_amt']], hdf5=res_path, dataset='neptune', override=True)

