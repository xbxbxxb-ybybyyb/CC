
import sys
sys.path.append('/data/group/800442/800319')
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/StrongStockModel')
from xquant.compute.aimr import AIMR
import json
from dataApi.sendInfo import send_message
from dataApi.tradeDate import get_recent_trade_date,get_pre_trade_date
para_list = list(range(1,9))#[(1,1,0)]+list(itertools.product([ 0.3,0.4,0.45,0.5,0.55, 0.6, 0.7, 0.8, 0.9], [0.1,0.15,0.2,0.25,0.3], [0]))

params = {
    "parallel_list": para_list,
    "tag":"xquant",
    "cpu":2,
    "gpu":0,
    "memory":1024*100,
    "preferred_gpu":0,
    'subtask_limit_num': 8
}

AIMR.runTasks('./generate_label/IntradayLabel_Bar8.py',json.dumps(params))
print("end")
send_message(['015664', '015614'],f'{get_pre_trade_date(get_recent_trade_date())}Nonfix label done')