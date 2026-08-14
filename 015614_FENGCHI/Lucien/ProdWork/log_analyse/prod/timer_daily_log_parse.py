# coding: utf-8
# Author：fengchi863
# Date ：2025/7/9 16:41

import sys
import os
sys.path.append('/data/user/015614/Lucien')

import datetime as dt
import subprocess
import time
from dataApi.sendInfo import send_message

root_path = '/data/user/015614/Lucien/ProdWork/log_analyse/prod/'

today_date = dt.date.today().strftime('%Y%m%d')
# today_date = '20250828'
envirment = 'prod UAT'

#%% 校验实盘日志是否都生成完成
today_date_str = today_date[:4] + '-' + today_date[4:6] + '-' + today_date[6:]
wait_log_fpath_list = [
    f'SHEX.EventDrivenCpp-{today_date_str}.log.gz',
    f'SZEX.EventDrivenCpp-{today_date_str}.log.gz',
    f'SHEX.JupiterStrategy-{today_date_str}.log.gz',
    f'SZEX.JupiterStrategy-{today_date_str}.log.gz',
    f'SHEX.MetisStrategy-{today_date_str}.log.gz',
    f'SZEX.MetisStrategy-{today_date_str}.log.gz',
    f'SHEX.LedaStrategy-{today_date_str}.log.gz',
    f'SZEX.LedaStrategy-{today_date_str}.log.gz',
    f'SHEX.SaturnStrategy-{today_date_str}.log.gz',
    f'SZEX.SaturnStrategy-{today_date_str}.log.gz',
    f'SHEX.MimasStrategy-{today_date_str}.log.gz',
    f'SZEX.MimasStrategy-{today_date_str}.log.gz',
    f'SHEX.SellStrategy-{today_date_str}.log.gz',
    f'SZEX.SellStrategy-{today_date_str}.log.gz',
    f'SHEX.CeresStrategy-{today_date_str}.log.gz',
    f'SZEX.CeresStrategy-{today_date_str}.log.gz',
    f'SHEX.UniTradeTool-{today_date_str}.log.gz',
    f'SZEX.UniTradeTool-{today_date_str}.log.gz',
]
prd_log_fpath_list = list(filter(lambda x: today_date_str in x, os.listdir('/data/group/800463/StrategyLog/prd/')))
for wait_fpath in wait_log_fpath_list:
    while wait_fpath not in prd_log_fpath_list:
        prd_log_fpath_list = list(filter(lambda x: today_date_str in x, os.listdir('/data/group/800463/StrategyLog/prd/')))
        send_message(f'实盘日志目前缺失{wait_fpath}')
        time.sleep(90)
print(f'{today_date_str}实盘日志全部就绪')

#%% 开始进行解析
# os.system(f'python3 {root_path}cpp/run_cpp_log_parse_daily.py {today_date} {envirment}')

# 这条在外面跑，覆盖原来文件的每日突破文件
os.system(f'python3 {root_path}unitradetool/utt_daily_log_parse.py {today_date} {envirment}')

program2_list = [
    f'python3 {root_path}cpp/run_cpp_log_parse_daily.py {today_date} {envirment}',
    f'python3 {root_path}metis/metis_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}saturn/saturn_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}leda/run_leda_log_parse_daily.py {today_date} {envirment}',
    f'python3 {root_path}jupiter/run_jupiter_log_parse_daily.py {today_date} {envirment}',
    f'python3 {root_path}jupiterBj/run_jupiterBj_log_parse_daily.py {today_date} {envirment}',
    f'python3 {root_path}ceres/ceres_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}p4/p4_daily_log_parse.py {today_date} {envirment}',
    f'python3 {root_path}mimas/mimas_daily_log_parse.py {today_date} {envirment}',
    # f'python3 {root_path}unitradetool/utt_daily_log_parse.py {today_date} {envirment}',
]

processes = [subprocess.Popen(program, shell=True) for program in program2_list]    # 都在1分钟之内
for process in processes:
    process.wait()