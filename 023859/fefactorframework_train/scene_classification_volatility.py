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

def update_xlsx(factor_list, upload_date):
    # df = pd.read_excel('/data/user/023859/factor_zooZZ/emotion_factor_inf.xlsx')
    new_factors = {
        "factor_name": [],
        "factor_type": [],
        "factor_owner": [],
        "提交时间": [],
        "emotion": [],
        "t": []
    }
    for factor in factor_list:
        new_factors['factor_name'].append(factor[7:])
        new_factors['factor_type'].append('SceneTick')
        new_factors['factor_owner'].append('tsq')
        new_factors['提交时间'].append(int(upload_date))
        new_factors['emotion'].append(np.nan)
        new_factors['t'].append('T-1')

    new_factors_df = pd.DataFrame(new_factors)
    df = new_factors_df
    # df = pd.concat([df, new_factors_df])
    df = df[['factor_name', 'factor_type', 'factor_owner', '提交时间', 'emotion', 't']]
    df.to_excel('/data/user/023859/factor_zooZZ/emotion_factor_inf_s1.xlsx', index=False)
    return

strategy_version = 20250526
start_date, end_date = 20170110,20241231

trading_days = s.tradingday(start_date, end_date)

strategy_path = f'/dfs/user/023859/neptune/{strategy_version}'
basic_file_path = '/dfs/user/023859/neptune/20250428/basic_file_zz1000_20160101_20250331.pkl' # zz1000基础样本
md_path = f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility'

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
periods_t_3 = [f't-3_{period}'for period in periods]

md = pd.concat(md)[['pre_close','open','close','amt','adjfactor']+periods].sort_index(level=['Ticker', 'dt'])

for period in periods:
    md[f't-1_{period}'] = md.groupby('Ticker')[f'{period}'].shift(1)
    md[f't-2_{period}'] = md.groupby('Ticker')[f'{period}'].shift(2)
    md[f't-3_{period}'] = md.groupby('Ticker')[f'{period}'].shift(3)

volatility_factor_df = basic_file.join(md[periods_t_1+periods_t_2+periods_t_3])
volatility_factor_df['tsq_newneptune_s1_scene_volatility'] = volatility_factor_df[periods_t_1+periods_t_2+periods_t_3].std(axis=1)

scene_factor_bank_inf_s1 = pd.DataFrame({'factor_name':['tsq_newneptune_s1_scene_volatility'],'factor_type':['SceneLast3Tick'],'factor_owner':['tsq'],'提交时间':['20250526'],'emotion':[""], 't':['T-1']})
scene_factor_bank_inf_s1.to_excel('/data/user/023859/factor_zooZZ/scene_factor_inf_s1.xlsx', index=False)

IO.pd_hdf5_writer(volatility_factor_df[['scene_volatility']], hdf5=f'/dfs/user/023859/neptune/{strategy_version}/scene_factors_volatility/{start_date}_{end_date}/tsq_newneptune_s1_scene_volatility.h5', dataset='neptune')
