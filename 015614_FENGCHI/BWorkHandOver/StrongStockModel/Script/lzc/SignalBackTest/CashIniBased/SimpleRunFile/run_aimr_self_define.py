# @Time : 2022/1/14 8:52
# @Author : Zhichen Lu
# @File : run_aimr_self_define.py

# @Time : 2021/12/30 14:14
# @Author : Zhichen Lu
# @File : run_aimr_factor_eval.py
import sys
sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
from dataApi.tradeDate import get_date_range, get_recent_trade_date, get_pre_trade_date

from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
import configparser
import os,time
import json
import itertools
import pandas as pd
import configparser
import datetime
TASK_NUM = 5
para_list = list(itertools.product([200, 300, 400, 500, 600], [0.005, 0.007, 0.01, 0.013, 0.015], [0.1, 0.2, 0.3, 0.4]))
i = 0
while para_list:

    now = datetime.datetime.now()
    HHMM = int(now.strftime('%H%M'))
    no_running_period = [(610, 930), (1555, 1915)]
    forbiden_period = False
    trading_day = get_recent_trade_date(int(now.strftime('%Y%m%d'))) == int(now.strftime('%Y%m%d'))
    if trading_day:
        for s, e in no_running_period:
            if HHMM > s and HHMM < e:
                forbiden_period = True

                delta_period = datetime.datetime(now.year,now.month,now.day, e//100, e%100) - datetime.datetime(now.year,now.month,now.day, HHMM//100, HHMM%100)
                print(f'---------------sleep until {datetime.datetime(now.year,now.month,now.day, e//100, e%100)} -------------------')
                time.sleep(delta_period.seconds+60)
                break

    aimr_para_list = para_list[:TASK_NUM]


    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),f'{len(aimr_para_list)} mission are now waiting')

    if not aimr_para_list:
        time.sleep(60*30)

    task_num = 99
    if trading_day:
        if HHMM<1915 and HHMM>930 and trading_day:
            task_num =70
    print('task_num',task_num)


    aimr_params = {
        "parallel_list": aimr_para_list[-task_num:],
        "tag":"xquant",
        "cpu":10,
        "gpu":0,
        "memory":1024*40,
        "preferred_gpu":0
    }
    aimr_multitimes.runTasks('./aimr/V_2_1pOOLsEEKING/run_backtestConsiderPredV4_2_1PoolSeeking.py',json.dumps(aimr_params))
    i+=1
    print(f'----------{i}----------')
    if len(para_list)>TASK_NUM:
        para_list = para_list[TASK_NUM:]
    else:
        para_list = []

