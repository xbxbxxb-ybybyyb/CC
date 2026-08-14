import pandas as pd
from h5data.IO import IO
import numpy as np
import os
from tqdm import tqdm
import decimal
from xquant.factordata import FactorData
from xquant.marketdata import MarketData
s = FactorData()
mdp = MarketData()

def round_(x, n=13):
    x = x + 1e-15
    if n > 0:
        res = float(decimal.Decimal(str(x)).quantize(decimal.Decimal('0.%s1' % ('0' * (n - 1))),rounding=decimal.ROUND_HALF_UP))
    else:
        res = int(decimal.Decimal(str(x)).quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_UP))
    return res

strategy_version = 20250606
start_date, end_date = 20170110,20241231
update_xlsx = False
trading_days = s.tradingday(20170101, end_date)

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_sc_20170110_20241231.pkl' # zz1000基础样本
res_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_swing/{start_date}_{end_date}'
os.makedirs(res_path, exist_ok=True)

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

index_df = pd.DataFrame(index=trading_days)

for date in tqdm(trading_days):
    tick_data = pd.read_pickle(f'/dfs/group/800463/data/index_data/ZZ1000/{date}'+'.pkl')
    tick_data = tick_data[(tick_data['MDTime'] >= 93000000)]
    tick_data_sc = tick_data[(tick_data['MDTime'] < 143000000)].iloc[-1]
    HighPx = tick_data['HighPx'].iloc[-1]
    LowPx = tick_data['LowPx'].iloc[-1]
    HighPx_sc = tick_data_sc['HighPx']
    LowPx_sc = tick_data_sc['LowPx']
    PreClosePx = tick_data['PreClosePx'].iloc[-1]
    index_df.loc[date, 'swing'] = (HighPx-LowPx) / PreClosePx
    index_df.loc[date, 'swing_sc'] = (HighPx_sc - LowPx_sc) / PreClosePx

index_df = index_df.rename_axis('dt')
index_df = index_df.reset_index()

index_df['dt'] = pd.to_datetime(index_df['dt'])
index_df['swing_t-1'] = index_df['swing'].shift(1)
index_df['swing_t-2'] = index_df['swing'].shift(2)
index_df['swing_t'] = index_df['swing_sc']
index_df['tsq_newneptune_sc_index_scene_swing'] = index_df[['swing_t-1','swing_t-2','swing_t']].mean(axis=1)
index_df['tsq_newneptune_sc_index_scene_swing'] = index_df['tsq_newneptune_sc_index_scene_swing'].fillna(0)

basic_file = basic_file.reset_index()
result_df = pd.merge(basic_file,index_df,on='dt',how='left').set_index(['dt','Ticker'])

if update_xlsx:
    scene_factor_bank_inf_sc = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx')
    scene_factor_bank_inf_append = pd.DataFrame({'factor_name':['tsq_newneptune_sc_index_scene_swing'],'factor_type':["['IndexLast2Tick', 'IndexTTick']"],'factor_owner':['tsq'],'提交时间':['20250527'],'emotion':[""], 't':['T']})
    scene_factor_bank_inf_sc = pd.concat([scene_factor_bank_inf_sc,scene_factor_bank_inf_append])
    scene_factor_bank_inf_sc.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx', index=False)

IO.pd_hdf5_writer(result_df[['tsq_newneptune_sc_index_scene_swing']], hdf5=os.path.join(res_path,'tsq_newneptune_sc_index_scene_swing.h5'), dataset='neptune')