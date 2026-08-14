# coding: utf-8
# Author：fengchi863
# Date ：2023/4/21 16:06
import sys
sys.path.append('/data/user/015614/Lucien')

from itertools import product
import os
from LucienUtil.SpeedUtil import SpeedUtil
from tqdm import tqdm

"""
第五区间去掉除pct外的分场景
"""

# period = ['period1', 'period2', 'period3', 'period4', 'period5', 'period6', 'period7']
# period = ['period1', 'period2']
period = ['period1', 'period1_roll']
# period = ['period1']
# period = ['period1', 'period2']
# period = ['period1', 'period2', 'period1_roll', 'period2_roll']
# period = ['period2', 'period2_roll']
# period = ['period3']
# period = ['period3', 'period3_roll']
# period = ['period4']
# period = ['period4', 'period4_roll']
# period = ['period5']
# period = ['period5', 'period5_roll']
# period = ['period6']
# period = ['period6', 'period6_roll']
# period = ['period7']
# period = ['period7', 'period7_roll']
# period = ['period8']
# period = ['period8', 'period8_roll']
fs_version = ['fsv8', 'fsv10', 'fsv11', 'fsrs', 'fsci']
# fs_version = ['fsv8', 'fsrs', 'rffs']
# fs_version = ['rffs']
# fs_version = ['fsv11', 'fsrs']
config_flag = [f'config{x}' for x in [1,2,3,4,5]]
label_trans = ['lt1']
# model_select = ['XgbRegModel', 'LgbRegModel']
model_select = ['XgbRegModel']
# model_select = ['LgbRegModel']
# hyper_search_mode = ['1']
hyper_search_mode = ['0']
# scaler_list = ['scaler1', 'scaler2']
scaler_list = ['scaler1']
attend_ratio = ['40']
seed = list(map(lambda x: str(x), list(range(0, 5))))
# seed = ['0']    # 0不在model_all里设置的范围内，所以应该是fix参数中的值

def wrapper(param_list):
    for param in tqdm(param_list):
        argv_list = ' '.join(list(param))
        os.system(f'python3 /data/user/015614/Lucien/Zeus/JupiterN/v3_0_1/scripts/model_all.py {argv_list}')

param_list = list(product(period, fs_version, config_flag, label_trans, model_select, scaler_list, hyper_search_mode, attend_ratio, seed))
param_list = list(filter(lambda x: x[1] + '_' + x[2] in ['fsv11_config5', 'fsv8_config5', 'fsrs_config1', 'fsci_config5'], param_list))
print(f'共训练{len(param_list)}个模型')
SpeedUtil.multiprocess(24, wrapper, param_list)
# wrapper([param_list[0]])