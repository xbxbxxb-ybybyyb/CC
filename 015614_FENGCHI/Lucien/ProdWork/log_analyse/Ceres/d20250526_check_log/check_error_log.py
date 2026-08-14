# coding: utf-8
# Author：fengchi863
# Date ：2025/5/26 16:20

import pandas as pd

log_path = '/data/user/013551/forXT/Ceres/log/'
date_list = [20241008, 20241009, 20241010, 20241011, 20241014]
# date_list = [20250227, 20250228, 20250303, 20250304, 20250305, 20250306, 20250307, 20250310]
univ = 'xdev'
type = 'type1'

for _dat in date_list:
    log_fpath = log_path + f'{_dat}_{type}.log'
    log_file = open(log_fpath)
    log_lines = log_file.readlines()
    log_lines = list(filter(lambda x: 'info' in str(x) and 'Thread' in str(x), log_lines))
    error_line = list()
    error_num = 0
    exception_line = list()
    exception_num = 0
    fail_line = list()
    fail_num = 0
    for line in log_lines:
        if 'Error' in line or 'error' in line:
            error_line.extend([line])
            error_num += 1
        if 'Exception' in line or 'exception' in line:
            exception_line.extend([line])
            exception_num += 1
        if 'Fail' in line or 'fail' in line:
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