# @Time : 2021/3/9 15:14
# @Author : Zhichen Lu
# @File : run_NNExtractor.py
import sys;

print('Python %s on %s' % (sys.version, sys.platform))
sys.path.extend(['/data/user/015614/MyWork', '/data/user/015614/MyWork/StrongStockModel', '/data/user/015614/MyWork/StrongStockModel/System', '/data/user/015614/MyWork/LimitUpPredStrategy', '/data/user/015614/MyWork/FaaMonitor', '/data/user/015614/MyWork/R2D2', '/data/user/015614/MyWork/CrossFT', '/data/user/015614/MyWork/CrossFT/basic', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211207定增上趋势股测试', '/data/user/015614/MyWork/ShortTermTrading/TradingPattern/baotuanqushigu/20211214测试趋势股卖出条件', '/data/user/015614/MyWork/SimiStock', '/data/user/015614/MyWork/GitProject/Factor', '/data/user/015614/MyWork/GitProject', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib', '/data/user/015614/MyWork/GitProject/Riskfolio-Lib/riskfolio', '/data/user/015614/MyWork/SimiStock/dataApi', '/data/user/015614/MyWork/ensemblemonitor-strategy-python', '/data/user/015614/MyWork/MillenniumFalcon', '/data/user/015614/MyWork'])

from StrongStockModel.model.Modelmpl.DTCOnline.FactorEvalByModel import aimr_multitimes
import configparser
import os
import pandas as pd
import json
fix_factor_list = pd.read_pickle('/data/group/800319/strategy_local_path_file/available_factor_list.pkl')
params = {
    "parallel_list": fix_factor_list,
    "tag": "xquant",
    "cpu": 1,
    "gpu": 0,
    "memory": 1024 * 70,
    "preferred_gpu": 0,
    'subtask_limit_num':20
}
import time

# time.sleep(70*60)
e = time.time()
aimr_multitimes.runTasks('/data/user/015664/TriggeredTrading/MillenniumFalcon/getMatrixNoReadingShiftSelfDefineAIMR.py', json.dumps(params))
print("end", time.time())
