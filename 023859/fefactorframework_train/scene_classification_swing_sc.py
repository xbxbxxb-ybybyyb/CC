import pandas as pd
import os
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

strategy_version = 20250606
start_date, end_date = 20170110, 20241231
update_xlsx = False

basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_sc_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_swing/{start_date}_{end_date}'
os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = IO.read_data([20160101,end_date],columns=['pre_close','high','low','amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['swing'] = (md['high'] - md['low'])/md['pre_close']
md.loc[md['zcz'],'swing'] = md.loc[md['zcz'],'swing'] / 2
md = md[md['amt']>0]
md = md.sort_index(level=['Ticker','dt'])
md['swing_t-1'] = md['swing'].groupby('Ticker').shift(1)
md['swing_t-2'] = md['swing'].groupby('Ticker').shift(2)

swing0 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20170110_20171231.pkl')
swing1 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20180101_20181231.pkl')
swing2 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20190101_20191231.pkl')
swing3 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20200101_20201231.pkl')
swing4 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20210101_20211231.pkl')
swing5 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20220101_20221231.pkl')
swing6 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20230101_20231231.pkl')
swing7 = pd.read_pickle(f'/dfs/user/023859/neptune/swing/swing_t_20240101_20241231.pkl')

data_swing_t = pd.concat([swing0,swing1,swing2,swing3,swing4,swing5,swing6,swing7]).sort_index()

basic_file['swing_t-1'] = md['swing_t-1']
basic_file['swing_t-2'] = md['swing_t-2']
basic_file['swing_t'] = data_swing_t['swing_t']

basic_file['tsq_newneptune_sc_scene_swing'] = basic_file[['swing_t-1','swing_t-2','swing_t']].mean(axis=1)
basic_file['tsq_newneptune_sc_scene_swing'] = basic_file['tsq_newneptune_sc_scene_swing'].fillna(0)

if update_xlsx:
    scene_factor_bank_inf_sc = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx')
    scene_factor_bank_inf_append = pd.DataFrame({'factor_name':['tsq_newneptune_sc_scene_swing'],'factor_type':["['T-1_Factor', 'MarketTTick']"],'factor_owner':['tsq'],'提交时间':['20250527'],'emotion':[""], 't':['T']})
    scene_factor_bank_inf_sc = pd.concat([scene_factor_bank_inf_sc,scene_factor_bank_inf_append])
    scene_factor_bank_inf_sc.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx', index=False)

IO.pd_hdf5_writer(basic_file[['tsq_newneptune_sc_scene_swing']], hdf5=os.path.join(res_path,'tsq_newneptune_sc_scene_swing.h5'), dataset='neptune')