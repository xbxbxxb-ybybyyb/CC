# @Time : 2022/3/7 18:18
# @Author : Zhichen Lu
# @File : run_aimr_condition.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import itertools,json
from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
from dataApi.sendInfo import send_message
from dataApi.tradeDate import get_recent_trade_date
import datetime
no_running_period = [(610, 900), (1555, 1700),(1830,1915)]

def get_forbidden_tag():
    now = datetime.datetime.now()
    HHMM = int(now.strftime('%H%M'))
    forbiden_period = False
    trading_day = get_recent_trade_date(int(now.strftime('%Y%m%d'))) == int(now.strftime('%Y%m%d'))
    if trading_day:
        for s, e in no_running_period:
            if HHMM > s and HHMM < e:
                forbiden_period = True
                break
    return forbiden_period



para_list = [(-1,1)]+list(itertools.product([round(x*0.001,3) for x in range(-20,21,4)], [0.05,0.1,0.15,0.2,0.25,0.3,0.35]))
para_list_stage1= [x+(0,) for x in para_list]
para_list_stage2 = [x+(1,) for x in para_list]


aimr_params0 = {
    "parallel_list": para_list_stage1,
    "tag":"xquant",
    "cpu":1,
    "gpu":0,
    "memory":1024*80,
    "preferred_gpu":0,
    'subtask_limit_num': 15
}

aimr_params1 = {
    "parallel_list": para_list_stage2,
    "tag":"xquant",
    "cpu":10,
    "gpu":0,
    "memory":1024*30,
    "preferred_gpu":0,
    'subtask_limit_num':8
}

aimr_multitimes.runTasks('./NonFix/run_backtest_V6_2_1.py',json.dumps(aimr_params0))
send_message(['015664'],'stage0 done')


if get_forbidden_tag():
    send_message(['015664'],'forbideen')
else:
    aimr_multitimes.runTasks('./NonFix/run_backtest_V6_2_1.py',json.dumps(aimr_params1))
    send_message(['015664'],'stage1 done')