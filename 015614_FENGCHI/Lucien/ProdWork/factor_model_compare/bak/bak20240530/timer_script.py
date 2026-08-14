# coding: utf-8
# Author：fengchi863
# Date ：2023/5/4 13:17

import sys
import os
sys.path.append('/data/user/015614/Lucien')
from xquant.factordata import FactorData
import datetime

fd = FactorData()

code_root_path = '/data/user/015614/Lucien/ProdWork/factor_model_compare/'

# 实盘
date = datetime.datetime.today().strftime('%Y%m%d')
# date = '20240426'
# env_list = 'UAT_lite'
# env_list = 'prod SHEX SZEX UAT UAT_50_51 UAT_49_53 UAT_lite'
env_list = 'prod UAT'
# env_list = 'UAT'
local_env_list = 'UAT'
# env_list = 'test'

os.system(f'python3 {code_root_path}jup_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jup_prod_model_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jup001_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jup001_prod_model_comparision.py {date} {env_list}')

# 20231101 Metis仿真  20231107 Metis实盘
os.system(f'python3 {code_root_path}metis_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}metis_prod_model_comparision.py {date} {env_list}')

# 20240301 Saturn实盘
os.system(f'python3 {code_root_path}pj2_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}pj2_prod_model_comparision.py {date} {env_list}')

# 20240401 leda 上线
os.system(f'python3 {code_root_path}leda_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}leda_prod_model_comparision.py {date} {env_list}')

# 20240306 jupiter cpp uat仿真
os.system(f'python3 {code_root_path}jup_uat_factor_comparision.py {date} {local_env_list}')
os.system(f'python3 {code_root_path}jup_uat_model_comparision.py {date} {local_env_list}')
