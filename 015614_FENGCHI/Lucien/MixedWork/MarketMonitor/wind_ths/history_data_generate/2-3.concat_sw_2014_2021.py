# coding: utf-8
# Author：fengchi863
# Date ：2022/9/5 16:37

"""
拼接2021版申万和2014版申万成分股
"""

import os
import pandas as pd
from tqdm import tqdm

path = '/data/user/015614/daily/basic/basic_wind_sw_history2/'
path_block = path + 'BlockData/'
path_industry = path + 'IndustryData/'

sw_2014_code_list = os.listdir(path_block + 'sw2014_each_block/')
sw_2021_code_list = os.listdir(path_block + 'sw2021_each_block/')

sw_all_code_list = list(set(sw_2014_code_list + sw_2021_code_list))

# 测试Wind的数据格式
# wind_data = pd.read_pickle(path_block + 'each_block/884030.WI.pkl')

for sw_code in tqdm(sw_all_code_list):
    tmp_sw2014data, tmp_sw2021data = pd.DataFrame(), pd.DataFrame()
    if sw_code in sw_2014_code_list:
        tmp_sw2014data = pd.read_pickle(path_block + f'sw2014_each_block/{sw_code}')
    if sw_code in sw_2021_code_list:
        tmp_sw2021data = pd.read_pickle(path_block + f'sw2021_each_block/{sw_code}')
    tmp_sw_data = pd.concat([tmp_sw2014data, tmp_sw2021data], axis=0)
    tmp_sw_data.to_pickle(path_block + f'each_block/{sw_code}')
