# @Time : 2021/1/13 13:06
# @Author : Zhichen Lu
# @File : offlineGenerateTimetablePercent.py
import sys, os

sys.path.append('/data/user/015664/TriggeredTrading/ensemblemonitor-strategy-python/')
sys.path.append('/data/user/015664/TriggeredTrading/')
import pandas as pd
from multiprocessing import Pool, Manager
from online_conf import alog_trading_distr_path
from StrongStockModel.conf.path_config import root_path
from tqdm import tqdm
from xquant.compute.aimr import AIMR

res = Manager().dict()
param = int(AIMR.getParam())
day = param

all_pool = pd.read_pickle(root_path + 'stock_pool_without_limit_up_down.pkl')
code_list = all_pool.loc[day]
code_list = code_list[code_list].index.tolist()
code_list = [str(x).zfill(6) + '.SZ' if x < 400000 else str(x) + '.SH' for x in code_list]
# code_list = pd.read_pickle(f'{code_list_path}/{str(day)}.pkl')
bar = tqdm(total=len(code_list))

if os.path.exists(f'{alog_trading_distr_path}{str(day)}.pkl'):
    raise Exception


def getOneStockTable(stk, date):
    # stk = '000001.SZ'
    # date = 20201026
    from offline.generateTimetable import getTargetPercentIntervalList

    timeTable = {}
    for sxw in ['1000', '1030', '1100', '1300', '1330', '1400', '1430']:
        timeTable[sxw] = getTargetPercentIntervalList(stk, date, period=20, sxw=sxw)
    res[stk] = timeTable
    # return timeTable


def update(*param):
    bar.update()
    bar.set_description()
    if bar.last_print_n == len(code_list):
        bar.close()


pool = Pool(16)
for each in code_list:
    pool.apply_async(getOneStockTable, (each, day,), callback=update)

pool.close()
pool.join()

res = res._getvalue()
pd.to_pickle(res, f'{alog_trading_distr_path}{str(day)}.pkl')
