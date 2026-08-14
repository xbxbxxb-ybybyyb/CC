# coding: utf-8
# Author：fengchi863
# Date ：2025/5/26 16:20

import pandas as pd

log_path = '/data/user/015614/shared/for_XT/Ceres/logs/20250617/'
# date_list = [20241008, 20241009, 20241010, 20241011, 20241014]
# date_list = [20250227, 20250228, 20250303, 20250304, 20250305, 20250306, 20250307, 20250310]
date_list = [20250516]
univ = 'xdev'
type = 'type1'

for _dat in date_list:
    log_fpath = log_path + f'{_dat}_{type}.log'
    log_file = open(log_fpath)
    log_lines = log_file.readlines()
    log_lines = list(filter(lambda x: 'algo' in str(x), log_lines))
    error_line = list()
    error_num = 0
    exception_line = list()
    exception_num = 0
    fail_line = list()
    fail_num = 0
    for line in log_lines:
        if 'error' in line.lower():
            error_line.extend([line])
            error_num += 1
        if 'exception' in line.lower():
            exception_line.extend([line])
            exception_num += 1
        if 'fail' in line.lower():
            fail_line.extend([line])
            fail_num += 1

    file_name = f'{_dat}_{type}_error.log'
    with open(log_path + file_name, 'w', encoding='utf-8') as outfile:
        for line in error_line:
            outfile.write(line + '\n')

    file_name = f'{_dat}_{type}_exception.log'
    with open(log_path + file_name, 'w', encoding='utf-8') as outfile:
        for line in exception_line:
            outfile.write(line + '\n')

    file_name = f'{_dat}_{type}_fail.log'
    with open(log_path + file_name, 'w', encoding='utf-8') as outfile:
        for line in fail_line:
            outfile.write(line + '\n')

    print(f'==========={_dat}_{type}===========')
    print(f'{error_num}  {exception_num}   {fail_num}')