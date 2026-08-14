import pandas as pd
from tqdm import tqdm
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

data_period4 = pd.read_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250513/factor_df_20170110_20220630.pkl')
start_date, end_date = 20170110,20220630

md = IO.read_data([start_date, end_date],columns=['pre_close'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
trading_days = s.tradingday(start_date, end_date)
ZZ1000_weight = []
for date in tqdm(trading_days):
    df_ZZ1000 = s.hset('INDEX',date,'ZZ1000',weightType=1) # 选择预估权重，避免回测用到未来数据
    ZZ1000_weight_date = pd.DataFrame(index = df_ZZ1000['stock'])
    ZZ1000_weight_date.index.names = ['stock']
    ZZ1000_weight_date['weight'] = df_ZZ1000.set_index('stock')['weight']/100
    ZZ1000_weight_date = ZZ1000_weight_date.reset_index()
    ZZ1000_weight_date['dt'] = pd.Timestamp(date)
    ZZ1000_weight_date = ZZ1000_weight_date.rename(columns={'stock':'Ticker'})
    ZZ1000_weight_date = ZZ1000_weight_date.set_index(['dt','Ticker'])[['weight']]
    ZZ1000_weight.append(ZZ1000_weight_date)

ZZ1000_weight = pd.concat(ZZ1000_weight, axis=0)

data_scene = pd.DataFrame(index=data_period4.index)
data_scene['scene'] = 0
data_scene['zcz'] = (((data_scene.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(data_scene.reset_index()['dt'] >= '2020-08-24')) | (data_scene.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
data_scene['pre_close'] = md['pre_close']

index0 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20160101_20191231.pkl')
index1 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20200101_20200630.pkl')
index2 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20200701_20201231.pkl')
index3 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20210101_20210630.pkl')
index4 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20210701_20211231.pkl')
index5 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20220101_20220630.pkl')
index6 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20220701_20221231.pkl')
index7 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20230101_20230630.pkl')
index8 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20230701_20231231.pkl')
index9 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20240101_20240630.pkl')
index10 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20240701_20241231.pkl')
index11 = pd.read_pickle('/dfs/user/023859/neptune/index_udl_weight_20250101_20250513.pkl')

data_index = pd.concat([index0,index1,index2,index3,index4,index5,index6,index7,index8,index9,index10,index11]).sort_index()
data_scene['price_1430'] = data_index['1430_price']
data_scene['pct'] = data_scene['price_1430'] / data_scene['pre_close'] - 1
data_scene.loc[data_scene['zcz'],'pct'] = data_scene.loc[data_scene['zcz'],'pct'] / 2

data_scene.loc[data_scene['pct']>0.03,'scene'] = 1
data_scene.loc[data_scene['pct']<-0.03,'scene'] = 2

data_period4['scene'] = data_scene['scene']
data_period4['weight'] = ZZ1000_weight['weight']
data_period4 = data_period4[data_period4['weight'] >= 0.0005]

data_period4[data_period4['scene'] == 1].drop(columns=['scene','weight']).to_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250513/factor_df_up3_20170110_20220630.pkl')
data_period4[data_period4['scene'] == 2].drop(columns=['scene','weight']).to_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250513/factor_df_down3_20170110_20220630.pkl')
data_period4[data_period4['scene'] == 0].drop(columns=['scene','weight']).to_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250513/factor_df_mid3_20170110_20220630.pkl')

