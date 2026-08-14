# coding: utf-8
# Author：fengchi863
# Date ：2020/6/1 17:00

from xquant.compute.aimr import AIMR
import json
import pandas as pd
print("start")

params = {
    "parallel_list": [1,2,3,4,5,6],
    "tag":"xquant",
    "cpu":10,
    "gpu":2,
    "memory":1200,
    "preferred_gpu":0
}

AIMR.runTasks('predict.py',json.dumps(params))
print("end")