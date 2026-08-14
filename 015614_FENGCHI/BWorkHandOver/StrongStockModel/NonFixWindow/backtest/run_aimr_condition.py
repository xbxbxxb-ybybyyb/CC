# @Time : 2022/3/7 18:18
# @Author : Zhichen Lu
# @File : run_aimr_condition.py

import sys

sys.path.append('/data/user/015664/TriggeredTrading/StrongStockModel/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import itertools,json
from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
from dataApi.sendInfo import send_message




para_list = list(itertools.product([ 0.3,0.4,0.5, 0.6, 0.7], [0.1,0.15,0.2,0.25,0.3], [-0.01, -0.005, 0, 0.005, 0.01]))
para_list_stage1= [x+(0,) for x in para_list]
para_list_stage2 = [x+(1,) for x in para_list]


aimr_params0 = {
    "parallel_list": para_list_stage1,
    "tag":"xquant",
    "cpu":1,
    "gpu":0,
    "memory":1024*60,
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

aimr_multitimes.runTasks('./PaperWork/run_backtest_hyper_seeking_threshold_per_amt.py',json.dumps(aimr_params0))
send_message(['015664'],'stage0 done')

aimr_multitimes.runTasks('./PaperWork/run_backtest_hyper_seeking_threshold_per_amt.py',json.dumps(aimr_params1))
send_message(['015664'],'stage1 done')
