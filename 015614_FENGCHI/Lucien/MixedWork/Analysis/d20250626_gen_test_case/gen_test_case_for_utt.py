# coding: utf-8
# Author：fengchi863
# Date ：2025/6/26 15:27

import pandas as pd
import numpy as np

trade_date = 20250306
ceres_samples_fpath = f'/data/group/800463/project/project3_prod/daily_data/{trade_date}_v4/ceres_factor_v4_{trade_date}.pkl'
p4_samples_fpath = f'/data/group/800463/project/project4_prod/daily_data/{trade_date}_v1/p4_factor_v1_{trade_date}.pkl'
mimas_samples_fpath = f'/data/group/800463/project/project2_prod/daily_data/{trade_date}_mimas_v1/mimas_factor_v1_{trade_date}.pkl'

type1_samples = pd.read_pickle(ceres_samples_fpath).index.get_level_values(1).tolist()
type2_samples = pd.read_pickle(p4_samples_fpath).index.get_level_values(1).tolist()
mimas_samples = pd.read_pickle(mimas_samples_fpath).index.get_level_values(1).tolist()

all_stock = list(set(type1_samples).union(set(type2_samples).union(mimas_samples)))

samples = pd.DataFrame(index=all_stock, columns=['type2', 'mimas', 'type1'])
samples['type2'] = samples.index.map(lambda x: x in type2_samples)
samples['mimas'] = samples.index.map(lambda x: x in mimas_samples)
samples['type1'] = samples.index.map(lambda x: x in type1_samples)
samples = samples.sort_index()

# samples.to_excel('/data/user/015614/junkData/samples20250306_2.xlsx')

jup_samples = pd.read_excel(f'/data/group/800463/日内强势股/jupiter_log_parse/因子耗时/因子耗时_2025-03-06_prod.xlsx', index_col=0)
samples['ZT_Time'] = samples.index.map(lambda x: jup_samples.loc[x, 'ZT_Time'] if x in jup_samples.index else '')