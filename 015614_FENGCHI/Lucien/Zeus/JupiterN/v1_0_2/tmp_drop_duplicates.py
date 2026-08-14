# coding: utf-8
# Author：fengchi863
# Date ：2023/2/1 21:20

import pandas as pd
from LucienUtil.FileUtil import FileUtil

out_begin = 20220101
out_end = 20220630
SUB_VERSION = 'v5'
valid_path_list = [
        # f'/data/user/015614/Zeus/pred/JupiterN/v1_0_2/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
        # f'/data/user/015614/Zeus/pred/JupiterN/v1_0_2/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}.csv',
        # f'/data/user/015614/Zeus/pred/JupiterN/v1_0_2/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}.csv',
        # f'/data/user/015614/Zeus/pred/JupiterN/v1_0_2/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_hml.csv',
        # f'/data/user/015614/Zeus/pred/JupiterN/v1_0_2/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_hml.csv',

        f'/data/user/015614/Zeus/pred/Europa/v1_0_32/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_32/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_32/LrRegModel/{out_begin}~{out_end}_LrRegModel_{SUB_VERSION}.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_32/LgbRegModel/{out_begin}~{out_end}_LgbRegModel_{SUB_VERSION}_hml.csv',
        f'/data/user/015614/Zeus/pred/Europa/v1_0_32/XgbRegModel/{out_begin}~{out_end}_XgbRegModel_{SUB_VERSION}_hml.csv'
]

for fpath in valid_path_list:
    check = pd.read_csv(fpath, index_col=0)
    droped_check = check.drop_duplicates()
    droped_check.to_csv(fpath)