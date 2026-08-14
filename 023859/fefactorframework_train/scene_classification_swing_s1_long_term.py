import pandas as pd
import os
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

strategy_version = 20250609
start_date, end_date = 20170110, 20241231
update_xlsx = True

basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_s1_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_swing/{start_date}_{end_date}'
os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = IO.read_data([20160101,end_date],columns=['pre_close','high','low','amt'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md['swing'] = (md['high'] - md['low'])/md['pre_close']
md.loc[md['zcz'],'swing'] = md.loc[md['zcz'],'swing'] / 2
md = md[md['amt']>0]
md['tsq_newneptune_s1_scene_swing_long_term'] = md['swing'].unstack().rolling(24,1).mean().stack()
md['tsq_newneptune_s1_scene_swing_long_term'] = md['tsq_newneptune_s1_scene_swing_long_term'].unstack().shift(1).stack()
# md = md.sort_index(level=['Ticker','dt'])
basic_file['tsq_newneptune_s1_scene_swing_long_term'] = md['tsq_newneptune_s1_scene_swing_long_term']
basic_file['tsq_newneptune_s1_scene_swing_long_term'] = basic_file['tsq_newneptune_s1_scene_swing_long_term'].fillna(0)

if update_xlsx:
    # scene_factor_bank_inf_s1 = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx')
    scene_factor_bank_inf_s1 = pd.DataFrame({'factor_name':['tsq_newneptune_s1_scene_swing_long_term'],'factor_type':["['T-1_Factor']"],'factor_owner':['tsq'],'提交时间':['20250606'],'emotion':[""], 't':['T-1']})
    # scene_factor_bank_inf_s1 = pd.concat([scene_factor_bank_inf_s1,scene_factor_bank_inf_append])
    scene_factor_bank_inf_s1.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx', index=False)

IO.pd_hdf5_writer(basic_file[['tsq_newneptune_s1_scene_swing_long_term']], hdf5=os.path.join(res_path,'tsq_newneptune_s1_scene_swing_long_term.h5'), dataset='neptune')



