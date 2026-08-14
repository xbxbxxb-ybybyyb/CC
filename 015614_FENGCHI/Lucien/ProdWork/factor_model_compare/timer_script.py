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
# date = '20250909'
# env_list = 'UAT_lite'
# env_list = 'prod SHEX SZEX UAT UAT_50_51 UAT_49_53 UAT_lite'
env_list = 'prod UAT'
# env_list = 'UAT'
prod_list = 'prod'
local_env_list = 'UAT'
# env_list = 'test'

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
# os.system(f'python3 {code_root_path}jup_uat_factor_comparision.py {date} {local_env_list}')
# os.system(f'python3 {code_root_path}jup_uat_model_comparision.py {date} {local_env_list}')

# 20240709 jupiter独立上线，europa加入科创板
# os.system(f'python3 {code_root_path}jup_prod_factor_comparision.py {date} {env_list}')
# os.system(f'python3 {code_root_path}jup_prod_model_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jup001_prod_factor_comparision.py {date} {prod_list}')
os.system(f'python3 {code_root_path}jup001_prod_model_comparision.py {date} {prod_list}')

# 20241217 jupiter_v10仿真上线
# os.system(f'python3 {code_root_path}jup_uat_factor_comparision.py {date} {local_env_list}')
# os.system(f'python3 {code_root_path}jup_uat_model_comparision.py {date} {local_env_list}')

# 20241224 jupiter_v10实盘上线
os.system(f'python3 {code_root_path}jup_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jup_prod_model_comparision.py {date} {env_list}')

# 20250101 Europa_v4仿真上线， 20250115 Europa_v4实盘上线
os.system(f'python3 {code_root_path}jup001_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jup001_prod_model_comparision.py {date} {env_list}')

# 20250120 jupiter北交所实盘上线
os.system(f'python3 {code_root_path}jupBj_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}jupBj_prod_model_comparision.py {date} {env_list}')

# 20250325 Saturn_v7仿真上线
# os.system(f'python3 {code_root_path}pj2_prod_factor_comparision_v7.py {date} {local_env_list}')
# os.system(f'python3 {code_root_path}pj2_prod_model_comparision_v7.py {date} {local_env_list}')
# 20250331 Saturn_v7实盘上线
os.system(f'python3 {code_root_path}pj2_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}pj2_prod_model_comparision.py {date} {env_list}')

# 20250530 Ceres实盘上线
os.system(f'python3 {code_root_path}ceres_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}ceres_prod_model_comparision.py {date} {env_list}')

# 20250530 P4实盘上线
os.system(f'python3 {code_root_path}p4_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}p4_prod_model_comparision.py {date} {env_list}')

# 20250801 Mimas仿真上线
os.system(f'python3 {code_root_path}mimas_prod_factor_comparision.py {date} {env_list}')
os.system(f'python3 {code_root_path}mimas_prod_model_comparision.py {date} {env_list}')


