import pandas as pd
from tqdm import tqdm
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

start_date, end_date = 20170110, 20240630
# data_period1 = pd.read_pickle(f'/data/group/800463/tangsq/neptune/20250526/factor_df_s1_20170110_20191231.pkl')
data_period1 = pd.read_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/20250526/factor_df_s1_20170110_20201231.pkl')
# data_period1 = pd.read_pickle(f'/dfs/user/023859/share_file/for_wj/neptune/20250513/factor_df_20170110_20220630.pkl')

md = IO.read_data([20160101,end_date],columns=['pre_close','high','low','amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['swing'] = (md['high'] - md['low'])/md['pre_close']
md.loc[md['zcz'],'swing'] = md.loc[md['zcz'],'swing'] / 2
md = md[md['amt']>0]
md = md.sort_index(level=['Ticker','dt'])
md['swing_t-1'] = md['swing'].groupby('Ticker').shift(1)
md['swing_t-2'] = md['swing'].groupby('Ticker').shift(2)

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
data_period1['weight'] = ZZ1000_weight['weight']
data_period1 = data_period1[data_period1['weight'] >= 0.0005]

# swing0 = pd.read_pickle(f'/dfs/user/023859/neptune/20250526/swing_t_931_20170110_20171231.pkl')
# swing1 = pd.read_pickle(f'/dfs/user/023859/neptune/20250526/swing_t_931_20180101_20181231.pkl')
# swing2 = pd.read_pickle(f'/dfs/user/023859/neptune/20250526/swing_t_931_20190101_20191231.pkl')
# swing3 = pd.read_pickle(f'/dfs/user/023859/neptune/20250526/swing_t_931_20200101_20201231.pkl')
swing0 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20170110_20171231.pkl')
swing1 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20180101_20181231.pkl')
swing2 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20190101_20191231.pkl')
swing3 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20200101_20201231.pkl')
swing4 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20210101_20211231.pkl')
swing5 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20220101_20221231.pkl')
swing6 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20230101_20231231.pkl')
swing7 = pd.read_pickle(f'/dfs/user/023859/neptune/20250513/swing/swing_t_20240101_20241231.pkl')

data_swing_t = pd.concat([swing0,swing1,swing2,swing3,swing4,swing5,swing6,swing7]).sort_index()

data_period1['swing_t'] = data_swing_t['swing_t']
data_period1['swing_t-1'] = md['swing_t-1']
data_period1['swing_t-2'] = md['swing_t-2']

data_period1['swing'] = data_period1[['swing_t','swing_t-1','swing_t-2']].mean(axis=1)
threshold = data_period1.loc[:pd.Timestamp('20201231')]['swing'].median()

data_period1['scene'] = 0
data_period1.loc[data_period1['swing'] >= threshold, 'scene'] = 1

data_period1.drop(columns=['weight','swing','swing_t','swing_t-1','swing_t-2']).to_pickle('/dfs/user/023859/share_file/for_wj/neptune/20250526/factor_df_s1_scene_filter_20170110_20201231.pkl')

# data_period1[data_period1['scene'] == 1].drop(columns=['weight','scene','swing','swing_t','swing_t-1','swing_t-2']).loc[:pd.Timestamp('20191231')].to_pickle('/data/group/800463/tangsq/neptune/20250526/factor_df_s1_scene_high_filter_20170110_20191231.pkl')
# data_period1[data_period1['scene'] == 0].drop(columns=['weight','scene','swing','swing_t','swing_t-1','swing_t-2']).loc[:pd.Timestamp('20191231')].to_pickle('/data/group/800463/tangsq/neptune/20250526/factor_df_s1_scene_low_filter_20170110_20191231.pkl')




