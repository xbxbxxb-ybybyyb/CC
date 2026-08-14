import pandas as pd
import os
from tqdm import tqdm
# from concurrent.futures import ThreadPoolExecutor
import IO

start_date, end_date = 20160101, 20191231
strategy_path = '/dfs/user/023859/neptune/20250428/'
basic_file_path = '/dfs/user/023859/neptune/20250428/basic_file_zz1000_20160101_20250331.pkl'
factor_check_path = '/data/user/023859/factor_zooZZ/factor_lib/check_res/check_res_tot_neptune_20250424.xlsx'
all_factor_path = '/data/user/023859/factor_zooZZ/all_factor/931'
label_path = '/dfs/user/023859/neptune/20250428/label_df_20160101_20250331.pkl'
factor_type_T_1 = "['T-1_Factor']","['xdb_tick1m']","['xdb_order1m']","['xdb_balancesheet_cs']","['xdb_cashflow_cs']","['xdb_income_cs']","['xdb_balancesheet']", "['xdb_cashflow']", "['xdb_income']]"
# 读取basic
basic_file = pd.read_pickle(basic_file_path)
basic_file = basic_file.loc[pd.to_datetime(str(start_date)):pd.to_datetime(str(end_date))]

# 可用因子列表
all_factor_inf = pd.read_excel('/data/user/023859/factor_zooZZ/all_factor_inf.xlsx')
factors_check_res = pd.read_excel(factor_check_path)
factors_available = factors_check_res[(factors_check_res['pre_check']=='pass')&(factors_check_res['factor_type'].isin(factor_type_T_1))]['factor_name'].to_list()
factor_bank_inf = all_factor_inf[all_factor_inf['factor_name'].isin(factors_available)]
factor_bank_inf = factor_bank_inf[['factor_name','factor_owner','factor_type','提交时间','emotion']]
factor_bank_inf['t'] = factor_bank_inf['factor_type'].apply(lambda x: 'T-1' if x in factor_type_T_1 else 'T')
factor_bank_inf.to_excel(strategy_path+'factor_bank_inf.xlsx', index=False)

factor_list = []

filenames = os.listdir(all_factor_path)
for file in tqdm(filenames):
    if file in factors_available:
        factor_path = os.path.join(all_factor_path,file,file+'.h5')
        factor = IO.read_data([start_date, end_date], alt=factor_path)
        factor_list.append(factor)

all_factors = pd.concat(factor_list,axis=1)
all_factor_df = basic_file.join(all_factors)

label_df = pd.read_pickle(label_path)

factor_df = all_factor_df.join(label_df)
factor_df = factor_df.dropna(subset=['label_t2o10dc'])
factor_df = factor_df[label_df.columns.tolist() + all_factor_df.columns.tolist()]
factor_df.to_pickle(strategy_path+f'factor_df_{start_date}_{end_date}.pkl')