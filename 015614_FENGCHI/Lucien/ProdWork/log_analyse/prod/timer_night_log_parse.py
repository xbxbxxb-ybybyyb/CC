# coding: utf-8
# Author：fengchi863
# Date ：2025/7/31 8:50

import os
import datetime as dt
import subprocess

root_path = '/data/user/015614/Lucien/ProdWork/log_analyse/prod/'

today_date = dt.date.today().strftime('%Y%m%d')
# today_date = '20250728'
envirment = 'night'

# os.system(f'python3 {root_path}cpp/run_cpp_log_parse_daily.py {today_date} {envirment}')
program2_list = [
    # f'python3 {root_path}cpp/run_cpp_log_parse_daily.py {today_date} {envirment}',
    # f'python3 {root_path}metis/metis_daily_log_parse.py {today_date} {envirment}',
    # f'python3 {root_path}saturn/saturn_daily_log_parse.py {today_date} {envirment}',
    # f'python3 {root_path}leda/run_leda_log_parse_daily.py {today_date} {envirment}',
    # f'python3 {root_path}jupiter/run_jupiter_log_parse_daily.py {today_date} {envirment}',
    # f'python3 {root_path}jupiterBj/run_jupiterBj_log_parse_daily.py {today_date} {envirment}',
    f'python3 {root_path}ceres/ceres_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}p4/p4_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}mimas/mimas_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}unitradetool/utt_daily_log_parse.py {today_date} {envirment}',
]

processes = [subprocess.Popen(program, shell=True) for program in program2_list]    # 都在1分钟之内
for process in processes:
    process.wait()