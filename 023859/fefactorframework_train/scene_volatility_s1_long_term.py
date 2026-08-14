import pandas as pd
import os
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

strategy_version = 20250609
start_date, end_date = 20170110, 20241231
update_xlsx = False

basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_s1_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility/{start_date}_{end_date}'
scene_factor_name = 'tsq_newneptune_s1_scene_volatility_long_term' # 分场景因子名称

os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = IO.read_data([20160101,end_date],columns=['pre_close','open','amt','adjfactor'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md = md[md['amt']>0]
md.loc[md['zcz'], 'open'] = ((md.loc[md['zcz'], 'open'] / md.loc[md['zcz'], 'pre_close'] - 1) / 2 + 1) * md.loc[md['zcz'], 'pre_close']
md['open'] = md['open'] * md['adjfactor']
md['pre_open'] = md['open'].unstack().shift(1).stack()
md['ret'] = md['open'] / md['pre_open'] - 1
md[scene_factor_name] = md['ret'].unstack().rolling(24,1).std().stack()
basic_file[scene_factor_name] = md[scene_factor_name]
basic_file[scene_factor_name] = basic_file[scene_factor_name].fillna(0)

if update_xlsx:
    scene_factor_bank_inf_s1 = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx')
    scene_factor_bank_inf_append = pd.DataFrame({'factor_name':[scene_factor_name],'factor_type':["scene_factor"],'factor_owner':['tsq'],'提交时间':['20250606'],'emotion':[""], 't':['T']})
    scene_factor_bank_inf_s1 = pd.concat([scene_factor_bank_inf_s1,scene_factor_bank_inf_append])
    scene_factor_bank_inf_s1.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx', index=False)

if os.path.exists(os.path.join(res_path,f'{scene_factor_name}.h5')):
    IO.pd_hdf5_writer(basic_file[[scene_factor_name]], hdf5=os.path.join(res_path,f'{scene_factor_name}.h5'), dataset='neptune', override=True)
else:
    IO.pd_hdf5_writer(basic_file[[scene_factor_name]], hdf5=os.path.join(res_path, f'{scene_factor_name}.h5'), dataset='neptune')


