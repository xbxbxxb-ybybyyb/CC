from h5data.IO import IO
import pandas as pd
import numpy as np
from tqdm import tqdm
import decimal
import os
import json
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
s = FactorData()
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
            # stockPool = list(set(zz1000_list) | set(s.hset('INDEX', date, 'ZZ500')['stock']) | set(
            #     s.hset('INDEX', date, 'HS300')['stock']))
            stockPool = list(set(zz1000_list))
        else:
            # stockPool = list(
            #     set(s.hset('INDEX', date, 'ZZ1000')['stock']) | set(s.hset('INDEX', date, 'ZZ500')['stock']) | set(
            #         s.hset('INDEX', date, 'HS300')['stock']))
            stockPool = list(set(s.hset('INDEX', date, 'ZZ1000')['stock']))
        stockPool_st_out = s.stock_filter(stockPool, date, 'STPT')['stock'].tolist()
        md_date = md.loc[pd.to_datetime(date)]
        filter_condition = ((md_date['list_len'] > 120) & (md_date['last_close_is_zt'] == 0) & (md_date['last_close_is_dt'] == 0))
            # filter_condition = (md_date['list_len'] > 120)
        market_available_stock_list = list(md_date[filter_condition].index)
        res[date] = list(set(stockPool_st_out) & set(market_available_stock_list))
        # res[date] = stockPool
    return res

strategy_version = 20250627
start_date, end_date = 20170110,20241231
start_date_ = int(s.tradingday(start_date,-250)[0])
end_date_ = int(s.tradingday(end_date,250)[-1])

price_1000_path = f'/dfs/user/023859/neptune/1000_price'
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
md_['Circu_Mkt_'] = (md_['float_shares'] * md_['close'])
md_ = md_[md_['amt']>0]
md_ = md_.sort_index(level=['Ticker', 'dt'])
md_['last_close_is_zt'] = md_.groupby('Ticker')['close_is_zt'].shift(1)
md_['last_close_is_dt'] = md_.groupby('Ticker')['close_is_dt'].shift(1)
md_['Circu_Mkt'] = md_.groupby('Ticker')['Circu_Mkt_'].shift(1)

# 股票换代码特殊处理
# md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'Circu_Mkt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'Circu_Mkt_']
# md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'last_close_is_zt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'close_is_zt']
# md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'last_close_is_dt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'close_is_dt']
#
# md_.loc[(pd.Timestamp('20181226'),'001872.SZ'),'Circu_Mkt'] = md_.loc[(pd.Timestamp('20181224'),'000022.SZ'),'Circu_Mkt_']
# md_.loc[(pd.Timestamp('20181226'),'001872.SZ'),'last_close_is_zt'] = md_.loc[(pd.Timestamp('20181224'),'000022.SZ'),'close_is_zt']
# md_.loc[(pd.Timestamp('20181226'),'001872.SZ'),'last_close_is_dt'] = md_.loc[(pd.Timestamp('20181224'),'000022.SZ'),'close_is_dt']

md_path = f'/dfs/user/023859/neptune/{strategy_version}/'
os.makedirs(md_path,exist_ok=True)

index_available_dict_sa = generate_neptune_basic_stocks_pool(start_date, end_date, md_)
mi_tuples = []
for date, stock_list in index_available_dict_sa.items():
    for stock in stock_list:
        mi_tuples.append((pd.to_datetime(date), stock))
filter_idx = pd.MultiIndex.from_tuples(mi_tuples, names=md_.index.names)
md_filtered = md_.loc[md_.index.intersection(filter_idx)]
md_filtered = md_filtered.sort_index()
neptune_basic_file_sa = md_filtered[['list_len','Circu_Mkt']]

price_1000 = []
filenames = os.listdir(price_1000_path)
for file in filenames:
    if file.endswith('.pkl'):
        price_1000.append(pd.read_pickle(os.path.join(price_1000_path,file)))
df_price_1000 = pd.concat(price_1000)
neptune_basic_file_sa = neptune_basic_file_sa.join(df_price_1000)
neptune_basic_file_sa['1000_is_zdt'] = ((neptune_basic_file_sa['1000_price']==neptune_basic_file_sa['ul_price']) | (neptune_basic_file_sa['1000_price']==neptune_basic_file_sa['dl_price']))
neptune_basic_file_sa = neptune_basic_file_sa[neptune_basic_file_sa['1000_is_zdt']==0]
neptune_basic_file_sa[['list_len','Circu_Mkt']].to_pickle(md_path+f'basic_file_zz1000_sa_{start_date}_{end_date}.pkl')
