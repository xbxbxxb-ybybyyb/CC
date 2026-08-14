# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from tqdm import tqdm
from LucienUtil.SpeedUtil import SpeedUtil
os.environ['CUDA_VISIBLE_DEVICES'] = '2'

PERIOD = ['period1', 'period2', 'period3']
# PERIOD = ['period4']
fs_version = ['fsv10', 'fsv11', 'fsrs']
# fs_version = ['fsv11']
# fs_version = ['rffs']
# fs_version = ['rffs', 'fsv8', 'fsv10', 'fsv11', 'fsrs']
label_flag = ['_pct_after']

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        # os.system(f'python3 /data/user/015614/Lucien/Zeus/Sapphire/v1_0_2/lgb_reg_model_no_emotion.py {argv_list}')
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Sapphire/v1_0_2/xgb_reg_model_no_emotion.py {argv_list}')
        # os.system(f'python3 /data/user/015614/Lucien/Zeus/Sapphire/v1_0_2/xgb_reg_model_generate_groudtruth.py {argv_list}')
#
param_list = list(product(PERIOD, fs_version, label_flag))
SpeedUtil.multiprocess(24, wrapper, param_list)

# SpeedUtil.multiprocess(1, wrapper, param_list)