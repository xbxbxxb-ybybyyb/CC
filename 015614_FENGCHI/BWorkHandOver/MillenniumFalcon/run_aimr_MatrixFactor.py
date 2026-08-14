# @Time : 2021/3/9 15:14
# @Author : Zhichen Lu
# @File : run_NNExtractor.py
from xquant.compute.aimr import AIMR
import configparser
import os
import json

params = {
    "parallel_list": list(range(20)),
    "tag":"xquant",
    "cpu":1,
    "gpu":0,
    "memory":1024*20,
    "preferred_gpu":0
}
import time

#time.sleep(70*60)
e = time.time()
AIMR.runTasks('./factor_preprocess/relation/getMatrixNoReadingShift.py',json.dumps(params))
print("end",time.time())

