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
from dataApi.sendInfo import send_message
from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
import configparser
import os,time
import json
import itertools
import pandas as pd
import configparser
import datetime
# TASK_NUM = 15
#para_list = list(itertools.product([200, 300, 400, 500, 600], [0.005, 0.007, 0.01, 0.013, 0.015], [0.1, 0.2, 0.3, 0.4]))
para_list0= [(-1,1,600,0.005,0.1)]+list(itertools.product([round(x * 0.001, 3) for x in range(-20, 21, 4)],
                            [0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4],
                            [ 600], [ 0.01, 0.015],
                            [0.2]))
para_list1 = [(1,)+x for x in para_list0]
para_list2 = [(2,)+x for x in para_list0]
# para_list = para_list1+para_list2
i = 0

while para_list1 or para_list2:

    now = datetime.datetime.now()
    HHMM = int(now.strftime('%H%M'))
    no_running_period = [(610, 900), (1555, 1915)]
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

    def deal_para_list(para_list,TASK_NUM):
        aimr_para_list = para_list[:TASK_NUM]
        if len(para_list)>TASK_NUM:
            para_list = para_list[TASK_NUM:]
        else:
            para_list = []
        return aimr_para_list,para_list

    if para_list1:
        a_para_list, para_list1 = deal_para_list(para_list1,20)
        c_num, mem = 1,50
    elif para_list2:
        a_para_list, para_list2 = deal_para_list(para_list2,6)
        c_num, mem = 10, 30
    else:
        continue

    print(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),f'{len(a_para_list)} mission are now waiting')

    if not a_para_list:
        send_message(['015664'],'done')
        time.sleep(60*30)


    aimr_params = {
        "parallel_list": a_para_list,
        "tag":"xquant",
        "cpu":c_num,
        "gpu":0,
        "memory":1024*mem,
        "preferred_gpu":0
    }
    aimr_multitimes.runTasks('./aimr/V4_2_1PoolSeekingReParamSeeking/run_backtestConsiderPredV6_2_1PoolSeekingReParamSeeking.py',json.dumps(aimr_params))
    i+=1
    print(f'----------{i}----------')


