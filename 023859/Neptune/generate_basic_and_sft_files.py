from h5data.IO import IO
import pandas as pd
import numpy as np
from tqdm import tqdm
import decimal
import os
import json
from xquant.factordata import FactorData
s = FactorData()

from xquant.marketdata import MarketData
mdp = MarketData()

def round_(x, n=0):
    x=x+1e-13
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

def generate_neptune_basic_stocks_pool(start_date, end_date, md):
    zz1000 = IO.read_data([start_date, end_date], columns=['index_1000'],
                          alt='/data/group/800080/warehouseJG/prod/UNIV/CHINA_STOCK/DAILY/OPTM/UNIV_CHINA_STOCK_DAILY_OPTM.h5')
    trading_days = s.tradingday(start_date, end_date)
    res = {}
    for date in tqdm(trading_days):
        if date < '20170101':
            zz1000_list = list(zz1000[zz1000['index_1000']].loc[pd.to_datetime(date)].index)
            # stockPool = list(set(zz1000_list))
            stockPool = list(set(zz1000_list) | set(s.hset('INDEX', date, 'ZZ500')['stock']) | set(
                s.hset('INDEX', date, 'HS300')['stock']))
        else:
            stockPool = list(
                set(s.hset('INDEX', date, 'ZZ1000')['stock']) | set(s.hset('INDEX', date, 'ZZ500')['stock']) | set(
                    s.hset('INDEX', date, 'HS300')['stock']))
            # stockPool = list(set(s.hset('INDEX', date, 'ZZ1000')['stock']))
        # stockPool_st_out = s.stock_filter(stockPool, date, 'STPT')['stock'].tolist()
        # md_date = md.loc[pd.to_datetime(date)]
        # filter_condition = (md_date['list_len'] > 120) # & (md_date['last_close_is_zt'] == 0) & (md_date['last_close_is_dt'] == 0)
        # market_available_stock_list = list(md_date[filter_condition].index)
        # res[date] = list(set(stockPool_st_out) & set(market_available_stock_list))
        res[date] = stockPool
    return res

start_date, end_date = 20160101,20241231
start_date_ = int(s.tradingday(start_date,-250)[0])
end_date_ = int(s.tradingday(end_date,250)[-1])

# 读取更长区间的全市场数据
md_ = IO.read_data([start_date_, end_date_],columns=['pre_close', 'open', 'high', 'low', 'close', 'amt', 'adjfactor'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
# 读取上市时间数据
ipo_data = IO.read_data([20000101, 20990101], alt='/data/group/800080/warehouse_event/prod/DATABASE/WIND/AShareDescription/AShareDescription.h5')
ipo_data = ipo_data.rename(columns={'S_INFO_LISTDATE': 'list_date', 'S_INFO_CODE': 'code'})
ipo_data = ipo_data.reset_index()
ipo_data = ipo_data[ipo_data['code'].apply(lambda x: x[:2] in ['60', '30', '00','68'])]  # 筛选上交所和深交所股票
ipo_data = ipo_data[~ipo_data['list_date'].isnull()]  # 去掉没有上市日期的股票，包括IPO终止和还未上市的股票
ipo_data['list_date'] = ipo_data['list_date'].apply(lambda x: pd.Timestamp(str(int(x))))
ipo_data['dt'] = ipo_data['list_date']
ipo_data['is_list_date'] = True
ipo_data = ipo_data.set_index(['dt', 'Ticker'])[['is_list_date']]

md_ = md_.join(ipo_data)
md_['after_list'] = md_['is_list_date'].unstack().fillna(method='ffill').stack()  # 上市后的标记
md_.loc[md_['amt'] == 0]['after_list'] = np.nan
md_['list_len'] = md_['after_list'].unstack().rolling(10000, 1).sum().stack()
md_.loc[(md_['list_len'].isnull() & (md_['amt'] > 0)), 'list_len'] = 250
md_['list_len'] = md_['list_len'].unstack().fillna(method='ffill').stack()
md_.loc[(md_['list_len'] > 250), 'list_len'] = 250

md_['zcz'] = (((md_.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md_.reset_index()['dt'] >= '2020-08-24')) | (md_.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md_['ul_price'] = md_['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md_['dl_price'] = md_['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md_.loc[md_['zcz'],'ul_price'] = md_.loc[md_['zcz'],'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md_.loc[md_['zcz'],'dl_price'] = md_.loc[md_['zcz'],'pre_close'].apply(lambda x: round_(x * 0.8, 2))

md_['close_is_zt'] = (md_['close']==md_['ul_price']).astype(float)
md_['close_is_dt'] = (md_['close']==md_['dl_price']).astype(float)
# 流通股本
md_['float_shares'] = IO.read_data([start_date_, end_date_], columns=['FLOAT_A_SHR_TODAY'], alt='/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
md_['Circu_Mkt'] = (md_['float_shares'] * md_['close'])
md_ = md_[md_['amt']>0]
md_ = md_.sort_index(level=['Ticker', 'dt'])
md_['last_close_is_zt'] = md_.groupby('Ticker')['close_is_zt'].shift(1)
md_['last_close_is_dt'] = md_.groupby('Ticker')['close_is_dt'].shift(1)
md_['Circu_Mkt'] = md_.groupby('Ticker')['Circu_Mkt'].shift(1)
md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'Circu_Mkt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'float_shares'] * md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'close']

# md1 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20160101_20161231.pkl')
# md2 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20170101_20171231.pkl')
# md3 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20180101_20181231.pkl')
# md4 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20190101_20191231.pkl')
# md5 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20200101_20201231.pkl')
# md6 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20210101_20211231.pkl')
# md = pd.concat([md1,md2,md3,md4,md5,md6])[['pre_close','close','amt','adjfactor','buy_931_1000_twap','sell_931_1000_twap']]

# md1 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20230601_20231231.pkl')
# md2 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20240101_20240630.pkl')
# md3 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20240701_20241231.pkl')
# md4 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20250101_20250416.pkl')
# md = pd.concat([md1,md2,md3,md4])[['pre_close','close','amt','adjfactor','buy_931_1000_twap','sell_931_1000_twap']]''
md_path = '/dfs/user/023859/neptune/'
# md = []
# filenames = os.listdir(md_path)
# for file in filenames:
#     if file.endswith('.pkl'):
#         md.append(pd.read_pickle(md_path+file))
#
# md = pd.concat(md)[['pre_close','close','amt','adjfactor','buy_1430_1455_twap','sell_0930_1000_twap']].sort_index()
# md = md.join(md_[['Circu_Mkt','list_len']])
# 处理数据集错误
# md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
# md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

# md['buy_1430_1455_twap_adj'] = md['buy_1430_1455_twap']*md['adjfactor']
# md['sell_0930_1000_twap_adj'] = md['sell_0930_1000_twap']*md['adjfactor']
#
# md['next_sell_0930_1000_twap_adj'] = md.groupby('Ticker')['sell_0930_1000_twap_adj'].apply(lambda x: x.shift(-1).bfill())
# md['next_3_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-3).bfill())
# md['next_5_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-5).bfill())

# md['label_t2o30dc'] = md['next_sell_0930_1000_twap_adj']/md['buy_1430_1455_twap_adj'] - 1
# md['label_t4o30d1'] = md['next_3_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
# md['label_t6o30d1'] = md['next_5_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1

# with open('/dfs/user/023859/share_file/for_wys/industry_hedging/index/zz1800可用股票列表_20160101_20201231.json','r') as file:
#     index_available_dict = json.load(file)
index_available_dict = generate_neptune_basic_stocks_pool(start_date, end_date, md_)

mi_tuples = []
for date, stock_list in index_available_dict.items():
    for stock in stock_list:
        mi_tuples.append((pd.to_datetime(date), stock))

filter_idx = pd.MultiIndex.from_tuples(mi_tuples, names=md_.index.names)
md_filtered = md_.loc[md_.index.intersection(filter_idx)]
md_filtered = md_filtered.sort_index()

neptune_basic_file = md_filtered[['list_len','Circu_Mkt']]
# neptune_sft_file = md_filtered[['list_len','Circu_Mkt','label_t2o30dc']].dropna()

# neptune_basic_file.dropna().to_pickle(md_path+f'basic_file_zz1800_{start_date}_{end_date}.pkl') # 689009.SH在20221206前没有行情
# neptune_sft_file.to_pickle(md_path+f'sft_basic_formal_931_{start_date}_{end_date}_all.pkl')


# factor_path_basic = f'/data/user/023859/factor_zooZZ/factor_lib/Basic_closed_hf_finish_{start_date}_{end_date}.h5'
# factor_path_sft =f'/data/user/023859/factor_zooZZ/factor_lib/sft_basic_formal_931_{start_date}_{end_date}.h5'
#
# if not os.path.exists(factor_path_basic):
#     IO.pd_hdf5_writer(neptune_basic_file, hdf5=factor_path_basic, dataset='neptune')
# else:
#     IO.pd_hdf5_writer(neptune_basic_file, hdf5=factor_path_basic, dataset='neptune', override=True)
#
# if not os.path.exists(factor_path_sft):
#     IO.pd_hdf5_writer(neptune_sft_file, hdf5=factor_path_sft, dataset='neptune')
# else:
#     IO.pd_hdf5_writer(neptune_sft_file, hdf5=factor_path_sft, dataset='neptune', override=True)

''' 样本内输出到公共路径
neptune_basic_file_in_sample = neptune_basic_file.loc[:pd.to_datetime('20191231')]
neptune_sft_file_in_sample = neptune_sft_file.loc[:pd.to_datetime('20191231')]

factor_path_basic_in_sample = '/data/group/800463/data/projectZZ_public/factor_lib/Basic_closed_hf_finish_20160101_20191231.h5'
factor_path_sft_in_sample ='/data/group/800463/data/projectZZ_public/factor_lib/sft_basic_formal_931_20160101_20191231.h5'

if not os.path.exists(factor_path_basic_in_sample):
    IO.pd_hdf5_writer(neptune_basic_file_in_sample, hdf5=factor_path_basic_in_sample, dataset='neptune')
else:
    IO.pd_hdf5_writer(neptune_basic_file_in_sample, hdf5=factor_path_basic_in_sample, dataset='neptune', override=True)

if not os.path.exists(factor_path_sft_in_sample):
    IO.pd_hdf5_writer(neptune_sft_file_in_sample, hdf5=factor_path_sft_in_sample, dataset='neptune')
else:
    IO.pd_hdf5_writer(neptune_sft_file_in_sample, hdf5=factor_path_sft_in_sample, dataset='neptune', override=True)
'''