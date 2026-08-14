# coding: utf-8
# Author：fengchi863
# Date ：2023/6/6 18:50

import sys
sys.path.append('/data/user/015614/Lucien')
import os
import subprocess

# TODO：先修改config.py文件，然后运行所有model_track_*.py文件

code_root_path = '/data/user/015614/Lucien/ProdWork/model_track/'

# os.system(f'python3 {code_root_path}model_track_jup.py')
# os.system(f'python3 {code_root_path}model_track_eur.py')
# os.system(f'python3 {code_root_path}model_track_saturn_20230807.py')
# os.system(f'python3 {code_root_path}model_track_sell1.py')
# os.system(f'python3 {code_root_path}model_track_sell3.py')
# os.system(f'python3 {code_root_path}model_track_jupz.py')
# os.system(f'python3 {code_root_path}model_track_metis.py')
# # os.system(f'python3 {code_root_path}model_track_ceres.py')    # 目前不用跟踪ceres

os.chdir('/data/user/015614/Lucien/')

program_list = [f'python3 {code_root_path}model_track_jup.py',
                f'python3 {code_root_path}model_track_eur.py',
                f'python3 {code_root_path}model_track_saturn_20230807.py',
                f'python3 {code_root_path}model_track_sell1.py',
                # f'python3 {code_root_path}model_track_sell3.py',
                f'python3 {code_root_path}model_track_jupz.py',
                f'python3 {code_root_path}model_track_metis.py',
                f'python3 {code_root_path}model_track_leda.py',
                # f'python3 {code_root_path}model_track_ceres.py',
                ]

processes = [subprocess.Popen(program, shell=True) for program in program_list]
for process in processes:
    process.wait()