# coding: utf-8
# Author：fengchi863
# Date ：2023/5/5 11:08

import sys
import os
sys.path.append('/data/user/015614/Lucien')
from dataApi.tradeDate import get_date_range

code_root_path = '/data/user/015614/Lucien/ProdWork/factor_model_compare/'

# 实盘
# 因子模型对比，某一天
# date_list = [20230608, 20230609, 20230612, 20230613]
# date_list = [20240306, 20240307]
# date_list = [20250227, 20250228, 20250303, 20250304, 20250305, 20250306, 20250307, 20250310]
# date_list = [20241008, 20241009, 20241010, 20241011, 20241014]
# date_list = [20250401, 20250402, 20241008, 20241009, 20241010]
date_list = [20250926]
# date_list = [20250714, 20250715, 20250716]
# from dataApi.tradeDate import get_date_range
# date_list = get_date_range(20250728, 20250730)
# env_list = 'SHEX SZEX'
# env_list = 'test_new'
# env_list = 'night'
# env_list = 'UAT'
# env_list = 'thread'
# env_list = 'test'
# env_list = 'night3'
# env_list = 'xdev'
env_list = 'prod UAT'
for date in date_list:
    # print('=======metis=======')
    # os.system(f'python3 {code_root_path}metis_prod_factor_comparision.py {date} {env_list}')
    # # print('=======metis=======')
    # os.system(f'python3 {code_root_path}metis_prod_model_comparision.py {date} {env_list}')
    print('=======jup001=======')
    # os.system(f'python3 {code_root_path}jup001_prod_factor_comparision.py {date} {env_list}')
    os.system(f'python3 {code_root_path}jup001_prod_model_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}jup_prod_factor_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}jup_prod_model_comparision.py {date} {env_list}')
    # print('=======sell=======')
    # os.system(f'python3 {code_root_path}sell_prod_factor_comparision.py {date} {env_list}')

    print('=======jup=======')
    # os.system(f'python3 {code_root_path}jup_uat_factor_comparision.py {date} {env_list}')
    print('=======pj2=======')
    # os.system(f'python3 {code_root_path}pj2_prod_factor_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}pj2_prod_model_comparision.py {date} {env_list}')
    #
    # print('=======jupiter model=======')
    # os.system(f'python3 {code_root_path}jup_uat_model_comparision.py {date} {env_list}')
    # print('=======jupiter001 model=======')
    # os.system(f'python3 {code_root_path}jup001_prod_model_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}jup_uat_model_comparision.py {date} {env_list}')
    # print('=======pj2 931 model=======')
    # os.system(f'python3 {code_root_path}pj2_931_prod_model_comparision.py {date} {env_list}')
    # print('=======pj2 931 sell1 local model=======')
    # os.system(f'python3 {code_root_path}pj2_931_sell1_prod_model_comparision.py {date} {env_list}')
    # print('=======pj2 931 sell3 local model=======')
    # os.system(f'python3 {code_root_path}pj2_931_sell3_prod_model_comparision.py {date} {env_list}')
    # print('=======jupz factor=======')
    # os.system(f'python3 {code_root_path}jupz_prod_factor_comparision.py {date} {env_list}')
    # print('=======jupz model=======')
    # os.system(f'python3 {code_root_path}jupz_prod_model_comparision.py {date} {env_list}')

    # os.system(f'python3 {code_root_path}metis_prod_factor_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}metis_prod_model_comparision.py {date} {env_list}')
    #
    # os.system(f'python3 {code_root_path}leda_prod_factor_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}leda_prod_model_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}jupBj_prod_factor_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}jupBj_prod_model_comparision.py {date} {env_list}')
    # os.system(f'python3 {code_root_path}ceres_prod_factor_comparision.py {date} {env_list}')
    os.system(f'python3 {code_root_path}ceres_prod_model_comparision.py {date} {env_list}')
    # #
    # os.system(f'python3 {code_root_path}p4_prod_factor_comparision.py {date} {env_list}')
    os.system(f'python3 {code_root_path}p4_prod_model_comparision.py {date} {env_list}')
    #
    # os.system(f'python3 {code_root_path}mimas_prod_factor_comparision.py {date} {env_list}')
    os.system(f'python3 {code_root_path}mimas_prod_model_comparision.py {date} {env_list}')
