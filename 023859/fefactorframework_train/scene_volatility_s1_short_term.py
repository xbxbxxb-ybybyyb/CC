import pandas as pd
import os
from h5data.IO import IO

strategy_version = 20250609
start_date, end_date = 20170110, 20241231
update_xlsx = False
scene_factor_name = 'tsq_newneptune_s1_scene_volatility_short_term' # 分场景因子名称
basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_s1_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility/{start_date}_{end_date}'
os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

minutes = ['m925','m955','m1025','m1055','m1125','m1325','m1355','m1425']
period_dict = {
    'ret_t-1_1430_t_open':['last_m1425','m925'],
    'ret_t-1_1400_t-1_1430':['last_m1355','last_m1425'],
    'ret_t-1_1330_t-1_1400':['last_m1325','last_m1355'],
    'ret_t-1_1300_t-1_1330':['last_m1125','last_m1325'],
    'ret_t-1_1100_t-1_1300':['last_m1055','last_m1125'],
    'ret_t-1_1030_t-1_1100':['last_m1025','last_m1055'],
    'ret_t-1_1000_t-1_1030':['last_m955','last_m1025'],
    'ret_t-1_930_t-1_1000':['last_m925','last_m955'],
}

md = IO.read_data([20160101,end_date],columns=['pre_close','amt','adjfactor'], alt='/data/group/800080/warehouseJG/prod/MD/CHINA_STOCK/DAILY/WIND/MD_CHINA_STOCK_DAILY_WIND.h5')
md['zcz'] = (((md.reset_index()['Ticker'].apply(lambda x: x[0] == '3'))&(md.reset_index()['dt'] >= '2020-08-24')) | (md.reset_index()['Ticker'].apply(lambda x: x[0:2] == '68'))).values
md = md[md['amt']>0]
open_px = IO.read_data([20160101,end_date],columns=minutes, alt='/data/group/800463/data/generalStrong/minute5/close.h5')
md = md.join(open_px)

for m in minutes:
    md.loc[md['zcz'], m] = ((md.loc[md['zcz'], m] / md.loc[md['zcz'], 'pre_close'] - 1) / 2 + 1) * md.loc[md['zcz'], 'pre_close']
    md[m] = md[m] * md['adjfactor']
    md[f'last_{m}'] = md[m].unstack().shift(1).stack()

for i, period in enumerate(period_dict):
    md[period] = md[period_dict[period][1]] / md[period_dict[period][0]] - 1
    basic_file[f'factor_ret_{i + 1}'] = md[period].unstack().shift(0).stack()
    basic_file[f'factor_ret_{i + 9}'] = md[period].unstack().shift(1).stack()
    basic_file[f'factor_ret_{i + 17}'] = md[period].unstack().shift(2).stack()

basic_file[scene_factor_name] = basic_file[[f'factor_ret_{i+1}' for i in range(24)]].std(axis=1)
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