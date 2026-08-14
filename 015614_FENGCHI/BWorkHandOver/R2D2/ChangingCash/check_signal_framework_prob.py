# @Time : 2022/3/28 15:56
# @Author : Zhichen Lu
# @File : check_signal_framework_prob.py
import pandas as pd
import os

base_path = '/data/group/800442/800319/Timing/ReportFactor/XuqiBacktest_Loop/intra_discount/'
file_list = os.listdir(base_path)
check1 = pd.read_pickle(f'{base_path}{file_list[0]}')
check2 = pd.read_pickle(f'{base_path}{file_list[5]}')
(check1!=check2).sum()
