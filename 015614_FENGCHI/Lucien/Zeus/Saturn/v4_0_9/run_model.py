# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from tqdm import tqdm
from LucienUtil.SpeedUtil import SpeedUtil

PERIOD = ['period1', 'period2', 'period3']
# PERIOD = ['period3']    # TODO: change this
fs_version = ['rffs', 'fsv8', 'fsv10', 'fsv11', 'fsrs']

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        # os.system(f'python3 /data/user/015614/Lucien/Zeus/Saturn/v4_0_9/xgb_reg_model.py {argv_list}')
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Saturn/v4_0_9/xgb_reg_model_all.py {argv_list}')

param_list = list(product(PERIOD, fs_version))
SpeedUtil.multiprocess(24, wrapper, param_list)

# SpeedUtil.multiprocess(1, wrapper, param_list[0])