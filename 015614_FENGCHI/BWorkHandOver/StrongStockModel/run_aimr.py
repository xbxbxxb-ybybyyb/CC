# @Time : 2021/3/24 14:29
# @Author : Zhichen Lu
# @File : run_aimr.py

# @Time : 2021/3/9 15:14
# @Author : Zhichen Lu
# @File : run_NNExtractor.py
from xquant.compute.aimr import AIMR
import json

mission_num = 50
para_list = [(m_id,mission_num) for m_id in range(mission_num)]

print(para_list)
params = {
    "parallel_list": para_list,
    "tag": "xquant",
    "cpu": 13,
    "gpu": 0,
    "memory": 1024 * 50,
    "preferred_gpu": 0
}

AIMR.runTasks('./Evaluation/DailyFactorFixEvaluation.py', json.dumps(params))
print("end")
