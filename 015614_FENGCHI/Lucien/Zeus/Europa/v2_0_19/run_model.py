# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from tqdm import tqdm
from LucienUtil.SpeedUtil import SpeedUtil
# os.environ['CUDA_VISIBLE_DEVICES'] = '0'
# os.environ['CUDA_VISIBLE_DEVICES'] = '1'
os.environ['CUDA_VISIBLE_DEVICES'] = '2'

PERIOD = ['period1', 'period2', 'period3']
# PERIOD = ['period6']    # TODO: change this
# fs_version = ['rffs', 'fsv8', 'fsv10', 'fsv11', 'fsrs']
fs_version = ['fsv8', 'fsv10', 'fsv11', 'fsrs']
emo_flag = ['_emotion', '_noEmotion']

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        # os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v2_0_19/lgb_reg_model_no_emotion.py {argv_list}')
        os.system(f'python3 /data/user/015614/Lucien/Zeus/Europa/v2_0_19/xgb_reg_model_no_emotion.py {argv_list}')
#
param_list = list(product(PERIOD, fs_version, emo_flag))
SpeedUtil.multiprocess(24, wrapper, param_list)

# SpeedUtil.multiprocess(1, wrapper, param_list)