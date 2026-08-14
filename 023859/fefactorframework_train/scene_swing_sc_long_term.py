import pandas as pd
import os
from h5data.IO import IO
from xquant.factordata import FactorData
s = FactorData()

strategy_version = 20250609
start_date, end_date = 20170110, 20241231
update_xlsx = False

basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_sc_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_swing/{start_date}_{end_date}'
scene_factor_name = 'tsq_newneptune_sc_scene_swing_long_term' # 分场景因子名称

os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

period = ['last_m1430','last_m1435','last_m1440','last_m1445','last_m1450','last_m1455','m925','m930','m935','m940','m945','m950','m955','m1000','m1005',\
          'm1010','m1015','m1020','m1025','m1030','m1035','m1040','m1045','m1050','m1055','m1100','m1105','m1110','m1115','m1120','m1125','m1300','m1305',\
          'm1310','m1315','m1320','m1325','m1330','m1335','m1340','m1345','m1350','m1355','m1400','m1405','m1410','m1415','m1420','m1425']

md = IO.read_data([20160101,end_date],columns=['pre_close','amt','adjfactor'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md = md[md['amt']>0]
high_px = IO.read_data([20160101,end_date], alt='/data/group/800463/data/generalStrong/minute5/high.h5')
low_px = IO.read_data([20160101,end_date], alt='/data/group/800463/data/generalStrong/minute5/low.h5')

minutes = list(high_px.columns)

md_high = md.join(high_px)
md_low = md.join(low_px)

for m in minutes:
    md_high[m] = md_high[m] * md_high['adjfactor']
    md_high.loc[md_high['zcz'], m] = ((md_high.loc[md_high['zcz'], m] / md_high.loc[md_high['zcz'], 'pre_close'] - 1) / 2 + 1) * md_high.loc[md_high['zcz'], 'pre_close']
    md_high[f'last_{m}'] = md_high[m].unstack().shift(1).stack()
    md_low[m] = md_low[m] * md_low['adjfactor']
    md_low.loc[md_low['zcz'], m] = ((md_low.loc[md_low['zcz'], m] / md_low.loc[md_low['zcz'], 'pre_close'] - 1) / 2 + 1) * md_low.loc[md_low['zcz'], 'pre_close']
    md_low[f'last_{m}'] = md_low[m].unstack().shift(1).stack()

md['swing'] = (md_high[period].max(axis=1) / md_low[period].min(axis=1)) - 1
basic_file[scene_factor_name] = md['swing'].unstack().rolling(24,1).mean().stack()
basic_file[scene_factor_name] = basic_file[scene_factor_name].fillna(0)

if update_xlsx:
    scene_factor_bank_inf_sc = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx')
    scene_factor_bank_inf_append = pd.DataFrame({'factor_name':[scene_factor_name],'factor_type':["scene_factor"],'factor_owner':['tsq'],'提交时间':['20250606'],'emotion':[""], 't':['T']})
    scene_factor_bank_inf_sc = pd.concat([scene_factor_bank_inf_sc,scene_factor_bank_inf_append])
    scene_factor_bank_inf_sc.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx', index=False)

if os.path.exists(os.path.join(res_path,f'{scene_factor_name}.h5')):
    IO.pd_hdf5_writer(basic_file[[scene_factor_name]], hdf5=os.path.join(res_path,f'{scene_factor_name}.h5'), dataset='neptune', override=True)
else:
    IO.pd_hdf5_writer(basic_file[[scene_factor_name]], hdf5=os.path.join(res_path, f'{scene_factor_name}.h5'), dataset='neptune')


