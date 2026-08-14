# coding: utf-8
# Author：fengchi863
# Date ：2024/10/16 15:32

import sys
import os
sys.path.append('/data/user/015614/Lucien')

code_root_path = '/data/user/015614/Lucien/MixedWork/MarketMonitor/wind_ths/daily_history_data_generate/'

os.system(f'python3 {code_root_path}1.wind_members.py')
os.system(f'python3 {code_root_path}2-1.Initialize_industrySW_2021.py')
os.system(f'python3 {code_root_path}2-2.Intitialize_industrySW_2014.py')
os.system(f'python3 {code_root_path}2-3.concat_sw_2014_2021.py')
os.system(f'python3 {code_root_path}3.concat_wind_sw.py')

