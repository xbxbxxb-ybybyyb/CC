import pandas as pd
import os
from h5data.IO import IO

strategy_version = 20250609
start_date, end_date = 20170110, 20241231
update_xlsx = False
scene_factor_name = 'tsq_newneptune_s1_scene_swing_mid_term' # 分场景因子名称
basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_s1_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_swing/{start_date}_{end_date}'
os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

period_dict = {
    'swing_t-1_1000_t_open':['last_m1000','last_m1005','last_m1010','last_m1015','last_m1020','last_m1025','last_m1030','last_m1035','last_m1040','last_m1045','last_m1050',\
                           'last_m1055','last_m1100','last_m1105','last_m1110','last_m1115','last_m1120','last_m1125','last_m1300','last_m1305','last_m1310','last_m1315',\
                           'last_m1320','last_m1325','last_m1330','last_m1335','last_m1340','last_m1345','last_m1350','last_m1355','last_m1400','last_m1405','last_m1410',\
                           'last_m1415','last_m1420','last_m1425','last_m1430','last_m1435','last_m1440','last_m1445','last_m1450','last_m1455','m925'],
    'swing_t-1_1030_t_1000':['last_m1030','last_m1035','last_m1040','last_m1045','last_m1050','last_m1055','last_m1100','last_m1105','last_m1110','last_m1115','last_m1120',\
                           'last_m1125','last_m1300','last_m1305','last_m1310','last_m1315','last_m1320','last_m1325','last_m1330','last_m1335','last_m1340','last_m1345',\
                           'last_m1350','last_m1355','last_m1400','last_m1405','last_m1410','last_m1415','last_m1420','last_m1425','last_m1430','last_m1435','last_m1440',\
                           'last_m1445','last_m1450','last_m1455','m925','m930','m935','m940','m945','m950','m955'],
    'swing_t-1_1100_t_1030':['last_m1100','last_m1105','last_m1110','last_m1115','last_m1120','last_m1125','last_m1300','last_m1305','last_m1310','last_m1315','last_m1320',\
                           'last_m1325','last_m1330','last_m1335','last_m1340','last_m1345','last_m1350','last_m1355','last_m1400','last_m1405','last_m1410','last_m1415',\
                           'last_m1420','last_m1425','last_m1430','last_m1435','last_m1440','last_m1445','last_m1450','last_m1455','m925','m930','m935','m940','m945','m950',\
                           'm955','m1000','m1005','m1010','m1015','m1020','m1025'],
    'swing_t-1_1300_t_1100':['last_m1300','last_m1305','last_m1310','last_m1315','last_m1320','last_m1325','last_m1330','last_m1335','last_m1340','last_m1345','last_m1350',\
                           'last_m1355','last_m1400','last_m1405','last_m1410','last_m1415','last_m1420','last_m1425','last_m1430','last_m1435','last_m1440','last_m1445',\
                           'last_m1450','last_m1455','m925','m930','m935','m940','m945','m950','m955','m1000','m1005','m1010','m1015','m1020','m1025','m1030','m1035','m1040',\
                           'm1045','m1050','m1055'],
    'swing_t-1_1330_t_1300':['last_m1330','last_m1335','last_m1340','last_m1345','last_m1350','last_m1355','last_m1400','last_m1405','last_m1410','last_m1415','last_m1420',\
                           'last_m1425','last_m1430','last_m1435','last_m1440','last_m1445','last_m1450','last_m1455','m925','m930','m935','m940','m945','m950','m955','m1000',\
                           'm1005','m1010','m1015','m1020','m1025','m1030','m1035','m1040','m1045','m1050','m1055','m1100','m1105','m1110','m1115','m1120','m1125'],
    'swing_t-1_1400_t_1330':['last_m1400','last_m1405','last_m1410','last_m1415','last_m1420','last_m1425','last_m1430','last_m1435','last_m1440','last_m1445','last_m1450',\
                           'last_m1455','m925','m930','m935','m940','m945','m950','m955','m1000','m1005','m1010','m1015','m1020','m1025','m1030','m1035','m1040','m1045',\
                           'm1050','m1055','m1100','m1105','m1110','m1115','m1120','m1125','m1300','m1305','m1310','m1315','m1320','m1325'],
    'swing_t-1_1430_t_1400':['last_m1430','last_m1435','last_m1440','last_m1445','last_m1450','last_m1455','m925','m930','m935','m940','m945','m950','m955','m1000','m1005',\
                           'm1010','m1015','m1020','m1025','m1030','m1035','m1040','m1045','m1050','m1055','m1100','m1105','m1110','m1115','m1120','m1125','m1300','m1305',\
                           'm1310','m1315','m1320','m1325','m1330','m1335','m1340','m1345','m1350','m1355'],
    'swing_t_930_t_1430':['m930','m935','m940','m945','m950','m955','m1000','m1005','m1010','m1015','m1020','m1025','m1030','m1035','m1040','m1045','m1050','m1055','m1100',\
                        'm1105','m1110','m1115','m1120','m1125','m1300','m1305','m1310','m1315','m1320','m1325','m1330','m1335','m1340','m1345','m1350','m1355','m1400','m1405',\
                        'm1410','m1415','m1420','m1425'],
}

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

for i, period in enumerate(period_dict):
    md[period] = (md_high[period_dict[period]].max(axis=1) / md_low[period_dict[period]].min(axis=1)) - 1
    basic_file[f'factor_swing_{i + 1}'] = md[period].unstack().shift(i).stack()
    basic_file[f'factor_swing_{i + 9}'] = md[period].unstack().shift(i+7).stack()
    basic_file[f'factor_swing_{i + 17}'] = md[period].unstack().shift(i+14).stack()

basic_file[scene_factor_name] = basic_file[[f'factor_swing_{i+1}' for i in range(24)]].mean(axis=1)
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