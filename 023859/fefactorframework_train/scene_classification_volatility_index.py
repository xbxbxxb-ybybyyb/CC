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

strategy_version = 20250527
start_date, end_date = 20170110,20241231
update_xlsx = True

trading_days = s.tradingday(20170101, end_date)

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = '/dfs/user/023859/neptune/20250428/basic_file_zz1000_20160101_20250331.pkl' # zz1000基础样本
md_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility'

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

index_df = pd.read_pickle(f'/dfs/user/023859/neptune/20250526/index_label_period_20160101_20241231.pkl')
index_df = index_df.droplevel(1)
periods = ['930_1000','1000_1030', '1030_1100','1100_1130','1300_1330','1330_1400','1400_1430','1430_1500']
periods_t_1 = [f't-1_{period}'for period in periods]
periods_t_2 = [f't-2_{period}'for period in periods]
periods_t_3 = [f't-3_{period}'for period in periods]

for period in periods:
    index_df[f't-1_{period}'] = index_df[f'{period}'].shift(1)
    index_df[f't-2_{period}'] = index_df[f'{period}'].shift(2)
    index_df[f't-3_{period}'] = index_df[f'{period}'].shift(3)

index_df['tsq_newneptune_s1_index_scene_volatility'] = index_df[periods_t_1+periods_t_2+periods_t_3].std(axis=1)
index_df = index_df.reset_index()
basic_file = basic_file.reset_index()
result_df = pd.merge(basic_file,index_df,on='dt',how='left').set_index(['dt','Ticker'])

if update_xlsx:
    scene_factor_bank_inf_s1 = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx')
    scene_factor_bank_inf_append = pd.DataFrame({'factor_name':['tsq_newneptune_s1_index_scene_volatility'],'factor_type':["['IndexLast3Tick']"],'factor_owner':['tsq'],'提交时间':['20250527'],'emotion':[""], 't':['T-1']})
    scene_factor_bank_inf_s1 = pd.concat([scene_factor_bank_inf_s1,scene_factor_bank_inf_append])
    scene_factor_bank_inf_s1.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx', index=False)

IO.pd_hdf5_writer(result_df[['tsq_newneptune_s1_index_scene_volatility']], hdf5=f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility/{start_date}_{end_date}/tsq_newneptune_s1_index_scene_volatility.h5', dataset='neptune')
