from h5data.IO import IO
import pandas as pd
import numpy as np
import os
from tqdm import tqdm
import decimal
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

start_date, end_date = 20160101,20241231
in_sample_end_date = 20201231

basic_df = pd.read_pickle('/dfs/user/023859/neptune/basic_file_neptune_all_20160101_20241231.pkl').loc[pd.Timestamp(str(start_date)):pd.Timestamp(str(end_date))]
basic_df['STPT'] = True
trading_days = s.tradingday(start_date, end_date)
for date in tqdm(trading_days):
    stockPool = list(basic_df.xs(pd.Timestamp(date), level=0).index)
    stockPool_st_out = s.stock_filter(stockPool, date, 'STPT')['stock'].tolist()
    mask = (basic_df.index.get_level_values(0) == pd.Timestamp(date)) & (basic_df.index.get_level_values(1).isin(stockPool_st_out))
    basic_df.loc[mask, 'STPT'] = False

start_date_ = int(s.tradingday(start_date,-500)[0])
end_date_ = int(s.tradingday(end_date,500)[-1])

# 读取更长区间的全市场数据
md_ = IO.read_data([start_date_, end_date_],columns=['pre_close', 'open', 'high', 'low', 'close', 'amt', 'adjfactor'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md_['zcz'] = (((md_.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md_.reset_index()['dt'] >= '2020-08-24')) | (md_.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md_['ul_price'] = md_['pre_close'].apply(lambda x: round_(x * 1.1, 2))
md_['dl_price'] = md_['pre_close'].apply(lambda x: round_(x * 0.9, 2))
md_.loc[md_['zcz'],'ul_price'] = md_.loc[md_['zcz'],'pre_close'].apply(lambda x: round_(x * 1.2, 2))
md_.loc[md_['zcz'],'dl_price'] = md_.loc[md_['zcz'],'pre_close'].apply(lambda x: round_(x * 0.8, 2))

md_['close_is_zt'] = (md_['close']==md_['ul_price']).astype(float)
md_['close_is_dt'] = (md_['close']==md_['dl_price']).astype(float)

# 流通股本
df_float_shares = IO.read_data([start_date_, end_date_], columns=['FLOAT_A_SHR_TODAY'], alt='/data/group/800080/warehouseJG/prod/DATABASE/WIND/AShareEODDerivativeIndicator/AShareEODDerivativeIndicator.h5')
md_['float_shares'] = df_float_shares['FLOAT_A_SHR_TODAY']
md_['Circu_Mkt'] = (md_['float_shares'] * md_['close'])
md_ = md_[md_['amt']>0]
md_ = md_.sort_index(level=['Ticker', 'dt'])
md_['last_close_is_zt'] = md_.groupby('Ticker')['close_is_zt'].shift(1)
md_['last_close_is_dt'] = md_.groupby('Ticker')['close_is_dt'].shift(1)
md_['Circu_Mkt'] = md_.groupby('Ticker')['Circu_Mkt'].shift(1)
md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'Circu_Mkt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'float_shares'] * md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'close']
md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'last_close_is_zt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'close_is_zt']
md_.loc[(pd.Timestamp('20191216'),'001914.SZ'),'last_close_is_dt'] = md_.loc[(pd.Timestamp('20191213'),'000043.SZ'),'close_is_dt']

md_.loc[(pd.Timestamp('20181226'),'001872.SZ'),'Circu_Mkt'] = df_float_shares.loc[(pd.Timestamp('20181220'),'001872.SZ'),'FLOAT_A_SHR_TODAY'] * md_.loc[(pd.Timestamp('20181220'),'000022.SZ'),'close']
md_.loc[(pd.Timestamp('20181226'),'001872.SZ'),'last_close_is_zt'] = md_.loc[(pd.Timestamp('20181220'),'000022.SZ'),'close_is_zt']
md_.loc[(pd.Timestamp('20181226'),'001872.SZ'),'last_close_is_dt'] = md_.loc[(pd.Timestamp('20181220'),'000022.SZ'),'close_is_dt']

basic_df[['Circu_Mkt','last_close_is_zt','last_close_is_dt']] = md_[['Circu_Mkt','last_close_is_zt','last_close_is_dt']]

# 计算标签
md1 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20160101_20161231.pkl')
md2 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20170101_20171231.pkl')
md3 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20180101_20181231.pkl')
md4 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20190101_20191231.pkl')
md5 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20200101_20201231.pkl')
md6 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20210101_20211231.pkl')
md7 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20220101_20221231.pkl')
md8 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20230101_20231231.pkl')
md9 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20240101_20241231.pkl')
md10 = pd.read_pickle(f'/dfs/user/023859/Hedging/index/md_20250101_20250331.pkl')

md = pd.concat([md1,md2,md3,md4,md5,md6,md7,md8,md9,md10])[['pre_close','close','amt','adjfactor','buy_931_1000_twap','sell_931_1000_twap']]

# md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
# md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['buy_931_1000_twap_adj'] = md['buy_931_1000_twap']*md['adjfactor']
md['sell_931_1000_twap_adj'] = md['sell_931_1000_twap']*md['adjfactor']
#
md['next_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-1).bfill())
md['next_3_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-3).bfill())
md['next_5_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-5).bfill())
md['next_10_sell_931_1000_twap_adj'] = md.groupby('Ticker')['sell_931_1000_twap_adj'].apply(lambda x: x.shift(-10).bfill())

md['label_t2o30d1'] = md['next_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
md['label_t4o30d1'] = md['next_3_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
md['label_t6o30d1'] = md['next_5_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1
md['label_t11o30d1'] = md['next_10_sell_931_1000_twap_adj']/md['buy_931_1000_twap_adj'] - 1

basic_df[['label_t2o30d1','label_t4o30d1','label_t6o30d1','label_t11o30d1']] = md[['label_t2o30d1','label_t4o30d1','label_t6o30d1','label_t11o30d1']]

md1 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20160101_20161231.pkl')
md2 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20170101_20171231.pkl')
md3 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20180101_20181231.pkl')
md4 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20190101_20191231.pkl')
md5 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20200101_20201231.pkl')
md6 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20210101_20211231.pkl')
md7 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20220101_20221231.pkl')
md8 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20230101_20231231.pkl')
md9 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20240101_20241231.pkl')
md10 = pd.read_pickle(f'/dfs/user/023859/neptune/label_0931_0941_s1/md_20250101_20250331.pkl')

md = pd.concat([md1,md2,md3,md4,md5,md6,md7,md8,md9,md10])[['pre_close','close','amt','adjfactor','buy_0931_0941_twap','sell_0931_0941_twap','buy_1000_1010_twap','sell_1000_1010_twap']]
#
# md.loc[(pd.Timestamp('20230905'),'601100.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'603338.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'605500.SH'),'adjfactor'] = np.nan
# md.loc[(pd.Timestamp('20230905'),'301349.SZ'),'adjfactor'] = np.nan
# md['adjfactor'] = md.groupby('Ticker')['adjfactor'].ffill()

md['buy_1000_1010_twap_adj'] = md['buy_1000_1010_twap']*md['adjfactor']
md['buy_1000_1010_twap_adj'] = md['buy_1000_1010_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['sell_1000_1010_twap_adj'] = md['sell_1000_1010_twap']*md['adjfactor']
md['sell_1000_1010_twap_adj'] = md['sell_1000_1010_twap_adj'].groupby('Ticker').apply(lambda x: x.bfill())

md['buy_931_941_twap_adj'] = md['buy_0931_0941_twap']*md['adjfactor']
md['sell_931_941_twap_adj'] = md['sell_0931_0941_twap']*md['adjfactor']

md['label_t2o10d1_pos'] = md['sell_1000_1010_twap_adj']/md['buy_931_941_twap_adj'] - 1
md['label_t2o10d1_neg'] = 1 - md['buy_1000_1010_twap_adj']/md['sell_931_941_twap_adj']

basic_df[['label_t2o10d1_pos','label_t2o10d1_neg']] = md[['label_t2o10d1_pos','label_t2o10d1_neg']]
basic_df_in_sample = basic_df.loc[:pd.Timestamp(str(in_sample_end_date))]

public_path_h5_in_sample = f'/dfs/group/800463/public/projectZZmkt_public/factor_lib/sft_basic_formal_931_{start_date}_{in_sample_end_date}.h5'
public_path_pkl_in_sample = f'/dfs/group/800463/public/projectZZmkt_public/factor_lib/sft_update_931_{start_date}_{in_sample_end_date}.pkl'

local_path_h5 = f'/data/user/023859/factor_zooZZmkt/factor_lib/sft_basic_formal_931_{start_date}_{end_date}.h5'
local_path_pkl = f'/data/user/023859/factor_zooZZmkt/factor_lib/sft_update_931_{start_date}_{end_date}.pkl'

# if not os.path.exists(public_path_h5_in_sample):
#     IO.pd_hdf5_writer(basic_df_in_sample, hdf5=public_path_h5_in_sample, dataset='neptune')
# else:
#     IO.pd_hdf5_writer(basic_df_in_sample, hdf5=public_path_h5_in_sample, dataset='neptune', override=True)

# basic_df_in_sample.to_pickle(public_path_pkl_in_sample)

if not os.path.exists(local_path_h5):
    IO.pd_hdf5_writer(basic_df, hdf5=local_path_h5, dataset='neptune')
else:
    IO.pd_hdf5_writer(basic_df, hdf5=local_path_h5, dataset='neptune', override=True)

basic_df.to_pickle(local_path_pkl)