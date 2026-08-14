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

strategy_version = 20250603
start_date, end_date = 20170110,20241231
update_xlsx = False

trading_days = s.tradingday(start_date, end_date)

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = f'/dfs/user/023859/neptune/{strategy_version}/basic_file_zz1000_sc_20170110_20241231.pkl' # zz1000基础样本
md_path = f'/dfs/user/023859/neptune/20250528/scene_factors_volatility'

basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

md = []
filenames = os.listdir(md_path)
for file in filenames:
    if file.endswith('.pkl'):
        md.append(pd.read_pickle(os.path.join(md_path,file)))

periods = ['930_1000','1000_1030', '1030_1100','1100_1130','1300_1330','1330_1400','1400_1430','1430_1500']
periods_t_1 = [f't-1_{period}'for period in periods]
periods_t_2 = [f't-2_{period}'for period in periods]
periods_t = ['930_1000','1000_1030', '1030_1100','1100_1130','1300_1330','1330_1400','1400_1430']

md = pd.concat(md)[periods+['pre_close_open']].sort_index(level=['Ticker', 'dt'])

for period in periods:
    md[f't-1_{period}'] = md.groupby('Ticker')[f'{period}'].shift(1)
    md[f't-2_{period}'] = md.groupby('Ticker')[f'{period}'].shift(2)

md['t_pre_close_open'] = md['pre_close_open']
md['t-1_pre_close_open'] = md.groupby('Ticker')['pre_close_open'].shift(1)

volatility_factor_df = basic_file.join(md[periods_t_1+periods_t_2+periods_t+['t_pre_close_open','t-1_pre_close_open']])
volatility_factor_df['tsq_newneptune_sc_scene_volatility'] = volatility_factor_df[periods_t_1+periods_t_2+periods_t+['t_pre_close_open','t-1_pre_close_open']].std(axis=1)
volatility_factor_df['tsq_newneptune_sc_scene_volatility'] = volatility_factor_df['tsq_newneptune_sc_scene_volatility'].fillna(0)

if update_xlsx:
    scene_factor_bank_inf_sc = pd.read_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx')
    scene_factor_bank_inf_append = pd.DataFrame({'factor_name':['tsq_newneptune_sc_scene_volatility'],'factor_type':"['MarketLast2Tick', 'MarketTTick']",'factor_owner':['tsq'],'提交时间':['20250527'],'emotion':[""], 't':['T']})
    scene_factor_bank_inf_sc = pd.concat([scene_factor_bank_inf_sc,scene_factor_bank_inf_append])
    scene_factor_bank_inf_sc.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_sc.xlsx', index=False)

IO.pd_hdf5_writer(volatility_factor_df[['tsq_newneptune_sc_scene_volatility']], hdf5=f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility/{start_date}_{end_date}/tsq_newneptune_sc_scene_volatility.h5', dataset='neptune', override=True)
