# coding: utf-8
# Author：fengchi863
# Date ：2021/12/30 8:42

'''
为了满足信息技术部的要求，缩小文件数量，把原来的npy文件存储到H5文件中
20211230版本，只存储20210101-20211130
'''

import sys
sys.path.append('/data/user/015614/MyWork')
sys.path.append('/data/user/015614/MyWork/ShortTermTrading')

import os
import h5py
import time
import pandas as pd
import numpy as np
from tqdm import tqdm
from ShortTermTrading.Util.tools import send_message

# TickData
root_path = '/arch1/group/800442/800319/LimitTickData2/'
to_save_path = '/arch1/group/800442/800319/H5LimitTickData2/'
dir_list = os.listdir(root_path)

for dir_name in dir_list:
    file_list = os.listdir(root_path + dir_name + '/')
    date_list = sorted(list(set(list(map(lambda x: (x[9:17]), file_list)))))
    date_list = list(filter(lambda x: '20210101' <= x <= '20211130', date_list))
    for dat in date_list:
        file_list2 = list(filter(lambda x: dat in x, file_list))
        print(len(file_list2))
        if not os.path.exists(os.path.dirname(to_save_path + f'{dir_name}/{dat}.h5')):
            os.makedirs(os.path.dirname(to_save_path + f'{dir_name}/'))
        with h5py.File(to_save_path + f'{dir_name}/{dat}.h5', 'w') as hf:
            for file_name in tqdm(file_list2):
                val = np.load(root_path + dir_name + '/' + file_name)
                # 重命名
                stk_code = file_name[:9]
                hf.create_dataset(f'{stk_code}', data=val)

send_message(['015614'], 'TickData转存已完成')

# TradeData
root_path = '/arch1/group/800442/800319/LimitTradeData2/'
to_save_path = '/arch1/group/800442/800319/H5LimitTradeData2/'
dir_list = os.listdir(root_path)

for dir_name in dir_list:
    file_list = os.listdir(root_path + dir_name + '/')
    date_list = sorted(list(set(list(map(lambda x: (x[9:17]), file_list)))))
    for dat in date_list:
        file_list2 = list(filter(lambda x: dat in x, file_list))
        print(len(file_list2))
        if not os.path.exists(os.path.dirname(to_save_path + f'{dir_name}/{dat}.h5')):
            os.makedirs(os.path.dirname(to_save_path + f'{dir_name}/'))
        with h5py.File(to_save_path + f'{dir_name}/{dat}.h5', 'w') as hf:
            for file_name in tqdm(file_list2):
                val = np.load(root_path + dir_name + '/' + file_name)
                # 重命名
                stk_code = file_name[:9]
                hf.create_dataset(f'f{stk_code}', data=val)

send_message(['015614'], 'TransactionData转存已完成')


# test read speed
# t1 = time.time()
# with h5py.File(root_path + 'date.h5', 'r') as hf:
#     val = hf['000002.SZ20210225.npy'][:]
#
# print(time.time() - t1)
#
# t1 = time.time()
# val = pd.read_hdf(root_path + 'date.h5') # h5py保存下来的读取不了
# print(time.time() - t1)
# print(val.shape)