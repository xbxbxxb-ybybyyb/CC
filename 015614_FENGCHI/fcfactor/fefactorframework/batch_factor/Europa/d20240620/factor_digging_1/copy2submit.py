# coding: utf-8
# Author：fengchi863
# Date ：2024/4/11 15:52

import shutil
import os
from tqdm import tqdm

submit_factors_name_list = [
    'fc_T1_n20240620_113',
    'fc_T1_n20240620_105',
    'fc_T1_n20240620_149',
    'fc_T1_n20240620_10',
    'fc_T1_n20240620_40',
    'fc_T1_n20240620_70',
]

d_date = os.getcwd().split('/')[-2]
digging_name = os.getcwd().split('/')[-1]
strategy_name = os.getcwd().split('/')[-3]
root_path = f'/data/user/015614/fcfactor/fefactorframework/batch_factor/{strategy_name}/{d_date}/{digging_name}/factor/'

for fname in tqdm(submit_factors_name_list):
    shutil.copyfile(root_path + f'factor_{fname}.py', f'/data/user/015614/fcfactor/New{strategy_name}/factor_20240711/factor_{fname}.py')